from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
import secrets
import httpx
from urllib.parse import urlencode, quote

from app.core.config import settings
from app.core.database import get_db
from app.security.jwt import create_access_token, verify_token
from app.security.hash import verify_password, create_password_hash
from app.services.user_service import UserOperations
from app.depend.current_user import get_current_user
from app.utils.validate_user_token import (
    validate_activation_token,
    create_activation_token,
    validate_reset_password_token,
    create_reset_password_token
)
from app.services.EMAIL_SERVICE.notification_service import NotificationService
from fastapi import Form
from fastapi.responses import HTMLResponse


router = APIRouter()
notification = NotificationService()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

MICROSOFT_AUTH_URL = f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/oauth2/v2.0/authorize"
MICROSOFT_TOKEN_URL = f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/oauth2/v2.0/token"
MICROSOFT_USERINFO_URL = "https://graph.microsoft.com/v1.0/me"

# ------------------- Activation, Password Reset (unchanged) -------------------
@router.get("/activate_user/{token}")
async def activate_user(token: str, db: AsyncSession = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing token")
    token_verify = await validate_activation_token(token)
    if not token_verify["valid"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    user_ops = UserOperations(db)
    user = await user_ops.get_user_by_id(token_verify["user_id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.is_active == 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already activated")
    await user_ops.update_user(user_id=user.id, is_active=1)
    await notification.send_welcome_activation_email(
        recipient_email=user.email,
        user_name=user.username
    )
    return {"message": "User activated successfully"}

@router.post("/request-password-reset")
async def request_password_reset(email: str, db: AsyncSession = Depends(get_db)):
    user_ops = UserOperations(db)
    user = await user_ops.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = await create_reset_password_token(user.id)
    await notification.send_reset_password_email(
        recipient_email=user.email,
        user_name=user.username,
        token=token
    )
    return {"message": "Password reset email sent"}

@router.get("/reset-password/{token}", response_class=HTMLResponse)
async def reset_password_page(token: str):
    return f"""
    <html>
        <body>
            <h2>Reset Password</h2>
            <form method="post" action="/auth/reset-password-submit">
                <input type="hidden" name="token" value="{token}" />
                <input type="password" name="password" placeholder="New password" required />
                <button type="submit">Reset Password</button>
            </form>
        </body>
    </html>
    """

@router.post("/reset-password-submit")
async def reset_password_submit(
    token: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    token_validate = await validate_reset_password_token(token)
    if not token_validate["valid"]:
        raise HTTPException(status_code=400, detail="Invalid token")
    user_ops = UserOperations(db)
    user = await user_ops.get_user_by_id(token_validate["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    hashed_password = await create_password_hash(password)
    await user_ops.update_user(user_id=user.id, password=hashed_password)
    return {"message": "Password reset successfully"}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user_ops = UserOperations(db)
    user = await user_ops.get_user_by_username(form_data.username)
    pass_verify = await verify_password(form_data.password, user.password) if user else False
    if not user or not pass_verify:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.is_active == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id, "username": user.username}

@router.get("/me")
async def read_users_me(current_user=Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if current_user.is_active == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User Not Active",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "picture": getattr(current_user, "picture", None)  # optional
    }

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
    db: AsyncSession = Depends(get_db)
):
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Google OAuth not configured")
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing authorization code")

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(GOOGLE_TOKEN_URL, data={
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        })
        if token_resp.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to exchange Google code")
        token_data = token_resp.json()
        userinfo_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
        if userinfo_resp.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to fetch Google user info")
        userinfo = userinfo_resp.json()

    email = userinfo.get("email")
    name = userinfo.get("name") or userinfo.get("given_name", email.split("@")[0] if email else "user")
    picture = userinfo.get("picture")  # Google profile image URL
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google account has no email")

    user_ops = UserOperations(db)
    user = await user_ops.get_user_by_email(email)

    if not user:

        username = name.replace(" ", "_").lower()
        if await user_ops.get_user_by_username(username):
            username = f"{username}_{secrets.token_hex(4)}"
        password_ = secrets.token_hex(32)
        user = await user_ops.create_oauth_user(
            username=username,
            email=email,
            password=await create_password_hash(password_),
            # is_active=1,
            # picture=picture
        )
        # Optionally send welcome email
        await notification.send_welcome_activation_email(
            recipient_email=email,
            user_name=user.username
        )
    # else:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="User already exists"
    #     )

    # Generate JWT
    access_token = await create_access_token(data={"sub": user.username})

    # Redirect to frontend OAuth callback with token and user info
    frontend_url = settings.DOMAIN.rstrip('/')
    redirect_url = (
        f"{frontend_url}/#/oauth-callback"
        f"?token={access_token}"
        f"&username={quote(user.username)}"
        f"&email={quote(user.email)}"
        f"&role={user.role}"
        f"&picture={quote(picture or '')}"
    )
    return RedirectResponse(url=redirect_url)

# ------------------- Microsoft OAuth -------------------
@router.get("/microsoft")
async def microsoft_login():
    if not settings.MICROSOFT_CLIENT_ID:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Microsoft OAuth not configured")
    params = {
        "client_id": settings.MICROSOFT_CLIENT_ID,
        "redirect_uri": settings.MICROSOFT_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile User.Read",
        "response_mode": "query",
    }
    return RedirectResponse(url=f"{MICROSOFT_AUTH_URL}?{urlencode(params)}")

@router.get("/microsoft/callback")
async def microsoft_callback(code: str, db: AsyncSession = Depends(get_db)):
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
    user = await user_ops.get_user_by_email(email)

    if not user:
        # Create new user
        username = name.replace(" ", "_").lower()
        if await user_ops.get_user_by_username(username):
            username = f"{username}_{secrets.token_hex(4)}"
        password_ = secrets.token_hex(32)
        user = await user_ops.create_oauth_user(
            username=username,
            email=email,
            password=await create_password_hash(password_),
            is_active=1
        )
        await notification.send_welcome_activation_email(
            recipient_email=email,
            user_name=user.username
        )
    # Microsoft Graph does not give photo in this basic call; we could fetch it separately, but skip for brevity

    access_token = await create_access_token(data={"sub": user.username})
    frontend_url = settings.DOMAIN.rstrip('/')
    redirect_url = (
        f"{frontend_url}/#/oauth-callback"
        f"?token={access_token}"
        f"&username={quote(user.username)}"
        f"&email={quote(user.email)}"
        f"&role={user.role}"
    )
    return RedirectResponse(url=redirect_url)