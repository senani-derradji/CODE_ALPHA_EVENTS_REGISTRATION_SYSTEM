from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.config import settings
from app.core.database import get_db
from app.security.jwt import create_access_token, verify_token
from app.security.hash import verify_password
from app.services.user_service import UserOperations
from app.depend.current_user import get_current_user
import httpx
from urllib.parse import urlencode


router = APIRouter()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

MICROSOFT_AUTH_URL = f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/oauth2/v2.0/authorize"
MICROSOFT_TOKEN_URL = f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/oauth2/v2.0/token"
MICROSOFT_USERINFO_URL = "https://graph.microsoft.com/v1.0/me"


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_ops = UserOperations(db)
    user = user_ops.get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id, "username": user.username}


@router.get("/me")
async def read_users_me(current_user=Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "email": current_user.email, "role": current_user.role}


@router.get("/google")
async def google_login():
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Google OAuth not configured")
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    return RedirectResponse(url=f"{GOOGLE_AUTH_URL}?{urlencode(params)}")

@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str = None,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback and display token in HTML"""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Google OAuth not configured")

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code"
        )

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(GOOGLE_TOKEN_URL, data={
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        })

        if token_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange Google code"
            )

        token_data = token_resp.json()

        userinfo_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )

        if userinfo_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch Google user info"
            )

        userinfo = userinfo_resp.json()

    email = userinfo.get("email")
    name = userinfo.get("name") or userinfo.get("given_name", email.split("@")[0] if email else "user")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account has no email"
        )

    user_ops = UserOperations(db)
    user = user_ops.get_user_by_email(email)

    if not user:
        import secrets
        username = name.replace(" ", "_").lower()
        if user_ops.get_user_by_username(username):
            username = f"{username}_{secrets.token_hex(4)}"

        user = user_ops.create_oauth_user(
            username=username,
            email=email,
            password=secrets.token_hex(32)
        )

    access_token = create_access_token(data={"sub": user.username})

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Google OAuth Success</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .token {{ background: #f0f0f0; padding: 10px; border-radius: 5px; word-break: break-all; }}
            .info {{ margin: 20px 0; padding: 15px; background: #e8f5e9; border-radius: 5px; }}
            button {{ padding: 10px 20px; margin-top: 20px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <h1>Google Login Successful!</h1>
        <div class="info">
            <h3>User Information:</h3>
            <p><strong>ID:</strong> {user.id}</p>
            <p><strong>Username:</strong> {user.username}</p>
            <p><strong>Email:</strong> {user.email}</p>
            <p><strong>Role:</strong> {user.role}</p>
        </div>
        <div>
            <h3>Access Token:</h3>
            <div class="token">{access_token}</div>
        </div>
        <button onclick="copyToken()">Copy Token</button>
        <br><br>
        <a href="/docs">📚 Go to API Documentation</a>

        <script>
            function copyToken() {{
                navigator.clipboard.writeText('{access_token}');
                alert('Token copied to clipboard!');
            }}
        </script>
    </body>
    </html>
    """

    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)


@router.get("/microsoft")
async def microsoft_login():
    if not settings.MICROSOFT_CLIENT_ID:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Microsoft OAuth not configured")
    from urllib.parse import urlencode
    params = {
        "client_id": settings.MICROSOFT_CLIENT_ID,
        "redirect_uri": settings.MICROSOFT_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile User.Read",
        "response_mode": "query",
    }
    return RedirectResponse(url=f"{MICROSOFT_AUTH_URL}?{urlencode(params)}")


@router.get("/microsoft/callback")
async def microsoft_callback(code: str, db: Session = Depends(get_db)):
    if not settings.MICROSOFT_CLIENT_ID:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Microsoft OAuth not configured")
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(MICROSOFT_TOKEN_URL, data={
            "code": code,
            "client_id": settings.MICROSOFT_CLIENT_ID,
            "client_secret": settings.MICROSOFT_CLIENT_SECRET,
            "redirect_uri": settings.MICROSOFT_REDIRECT_URI,
            "grant_type": "authorization_code",
            "scope": "openid email profile User.Read",
        })
        if token_resp.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to exchange Microsoft code")
        token_data = token_resp.json()
        userinfo_resp = await client.get(MICROSOFT_USERINFO_URL, headers={"Authorization": f"Bearer {token_data['access_token']}"})
        if userinfo_resp.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to fetch Microsoft user info")
        userinfo = userinfo_resp.json()

    email = userinfo.get("mail") or userinfo.get("userPrincipalName")
    name = userinfo.get("displayName") or (email.split("@")[0] if email else None)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Microsoft account has no email")

    user_ops = UserOperations(db)
    user = user_ops.get_user_by_email(email)
    if not user:
        import secrets
        user = user_ops.create_oauth_user(username=name, email=email, password=secrets.token_hex(32))

    access_token = create_access_token(data={"sub": user.username})
    return RedirectResponse(url=f"{settings.FRONTEND_URL}?token={access_token}")
