from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
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

router = APIRouter()
notification = NotificationService()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

MICROSOFT_AUTH_URL = f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/oauth2/v2.0/authorize"
MICROSOFT_TOKEN_URL = f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/oauth2/v2.0/token"
MICROSOFT_USERINFO_URL = "https://graph.microsoft.com/v1.0/me"

# Helper function to generate HTML responses
def html_response(message: str, title: str = "Message", status_code: int = 200) -> HTMLResponse:
    return HTMLResponse(
        content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f5f5f5;
                }}
                .container {{
                    text-align: center;
                    padding: 2rem;
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .success {{
                    color: #4CAF50;
                }}
                .error {{
                    color: #f44336;
                }}
                button {{
                    margin-top: 1rem;
                    padding: 10px 20px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }}
                button:hover {{
                    background-color: #45a049;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{title}</h1>
                <p>{message}</p>
                <button onclick="window.location.href='/'">Go to Home</button>
            </div>
        </body>
        </html>
        """,
        status_code=status_code
    )

def error_html_response(message: str, title: str = "Error", status_code: int = 400) -> HTMLResponse:
    return HTMLResponse(
        content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f5f5f5;
                }}
                .container {{
                    text-align: center;
                    padding: 2rem;
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .error {{
                    color: #f44336;
                }}
                button {{
                    margin-top: 1rem;
                    padding: 10px 20px;
                    background-color: #f44336;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }}
                button:hover {{
                    background-color: #d32f2f;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="error">{title}</h1>
                <p>{message}</p>
                <button onclick="window.location.href='/'">Go to Home</button>
            </div>
        </body>
        </html>
        """,
        status_code=status_code
    )

# ------------------- Activation, Password Reset -------------------
@router.get("/activate_user/{token}", response_class=HTMLResponse)
async def activate_user(token: str, db: AsyncSession = Depends(get_db)):
    if not token:
        return error_html_response("Missing token", "Activation Failed")

    token_verify = await validate_activation_token(token)
    if not token_verify["valid"]:
        return error_html_response("Invalid token", "Activation Failed")

    user_ops = UserOperations(db)
    user = await user_ops.get_user_by_id(token_verify["user_id"])
    if not user:
        return error_html_response("User not found", "Activation Failed")

    if user.is_active == 1:
        return error_html_response("User already activated", "Activation Failed")

    await user_ops.update_user(user_id=user.id, is_active=1)
    await notification.send_welcome_activation_email(
        recipient_email=user.email,
        user_name=user.username
    )

    return html_response(f"Welcome {user.username}! Your account has been activated successfully.", "Account Activated")

class PasswordResetRequestBody(BaseModel):
    email: str

@router.post("/request-password-reset")
async def request_password_reset(body: PasswordResetRequestBody, db: AsyncSession = Depends(get_db)):
    user_ops = UserOperations(db)
    user = await user_ops.get_user_by_email(body.email)
    if not user:
        # Don't reveal if user exists for security, but still return success
        return JSONResponse(content={"message": "If that email exists, a reset link has been sent."})

    token = await create_reset_password_token(user.id)
    await notification.send_reset_password_email(
        recipient_email=user.email,
        user_name=user.username,
        token=token
    )

    return JSONResponse(content={"message": "Password reset email has been sent. Please check your inbox."})

@router.get("/reset-password/{token}", response_class=HTMLResponse)
async def reset_password_page(token: str):
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reset Password</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #f5f5f5;
            }}
            .container {{
                text-align: center;
                padding: 2rem;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                width: 300px;
            }}
            input {{
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
            }}
            button {{
                width: 100%;
                padding: 10px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }}
            button:hover {{
                background-color: #45a049;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Reset Password</h2>
            <form method="post" action="/auth/reset-password-submit">
                <input type="hidden" name="token" value="{token}" />
                <input type="password" name="password" placeholder="New password" required />
                <button type="submit">Reset Password</button>
            </form>
        </div>
    </body>
    </html>
    """)

class PasswordResetSubmitBody(BaseModel):
    token: str
    new_password: str
    confirm_password: str

@router.post("/reset-password-submit")
async def reset_password_submit(
    body: PasswordResetSubmitBody,
    db: AsyncSession = Depends(get_db)
):
    if body.new_password != body.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    token_validate = await validate_reset_password_token(body.token)
    if not token_validate["valid"]:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user_ops = UserOperations(db)
    user = await user_ops.get_user_by_id(token_validate["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = await create_password_hash(body.new_password)
    await user_ops.update_user(user_id=user.id, password=hashed_password)

    return JSONResponse(content={"message": "Password has been reset successfully."})

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user_ops = UserOperations(db)
    # Accept both username and email in the username field
    user = await user_ops.get_user_by_username(form_data.username)
    if not user:
        user = await user_ops.get_user_by_email(form_data.username)
    pass_verify = await verify_password(form_data.password, user.password) if user else False

    if not user or not pass_verify:
        raise HTTPException(status_code=401, detail="Incorrect credentials")

    if user.is_active == 0:
        raise HTTPException(status_code=401, detail="Account not active. Please check your email to activate your account.")

    access_token = await create_access_token(data={"sub": user.username})

    return JSONResponse(content={"access_token": access_token, "token_type": "bearer"})

@router.get("/me")
async def read_users_me(current_user=Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    if current_user.is_active == 0:
        raise HTTPException(status_code=401, detail="User Not Active")

    return JSONResponse(content={
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "full_name": getattr(current_user, "full_name", None),
        "bio": getattr(current_user, "bio", None),
        "phone": getattr(current_user, "phone", None),
        "profile_picture": getattr(current_user, "profile_picture", getattr(current_user, "picture", None)),
        "is_active": bool(current_user.is_active),
        "is_verified": bool(getattr(current_user, "is_verified", False)),
        "created_at": str(getattr(current_user, "created_at", "")) or "",
        "updated_at": str(getattr(current_user, "updated_at", "")) if getattr(current_user, "updated_at", None) else None,
    })

@router.get("/google", response_class=RedirectResponse)
async def google_login():
    if not settings.GOOGLE_CLIENT_ID:
        return error_html_response("Google OAuth not configured", "Configuration Error", 501)

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    return RedirectResponse(url=f"{GOOGLE_AUTH_URL}?{urlencode(params)}")

@router.get("/google/callback", response_class=RedirectResponse)
async def google_callback(
    request: Request,
    code: str = None,
    db: AsyncSession = Depends(get_db)
):
    if not settings.GOOGLE_CLIENT_ID:
        return error_html_response("Google OAuth not configured", "Configuration Error", 501)

    if not code:
        return error_html_response("Missing authorization code", "Authentication Failed", 400)

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(GOOGLE_TOKEN_URL, data={
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        })
        if token_resp.status_code != 200:
            return error_html_response("Failed to exchange Google code", "Authentication Failed", 400)

        token_data = token_resp.json()
        userinfo_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
        if userinfo_resp.status_code != 200:
            return error_html_response("Failed to fetch Google user info", "Authentication Failed", 400)

        userinfo = userinfo_resp.json()

    email = userinfo.get("email")
    name = userinfo.get("name") or userinfo.get("given_name", email.split("@")[0] if email else "user")
    picture = userinfo.get("picture")

    if not email:
        return error_html_response("Google account has no email", "Authentication Failed", 400)

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
        )
        await notification.send_welcome_activation_email(
            recipient_email=email,
            user_name=user.username
        )

    access_token = await create_access_token(data={"sub": user.username})

    frontend_url = settings.DOMAIN.rstrip('/')
    redirect_url = (
        f"{frontend_url}"
        f"?token={access_token}"
        f"&username={quote(user.username)}"
        f"&email={quote(user.email)}"
        f"&role={user.role}"
        f"&picture={quote(picture or '')}"
    )
    return RedirectResponse(url=redirect_url)

# ------------------- Microsoft OAuth -------------------
@router.get("/microsoft", response_class=RedirectResponse)
async def microsoft_login():
    if not settings.MICROSOFT_CLIENT_ID:
        return error_html_response("Microsoft OAuth not configured", "Configuration Error", 501)

    params = {
        "client_id": settings.MICROSOFT_CLIENT_ID,
        "redirect_uri": settings.MICROSOFT_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile User.Read",
        "response_mode": "query",
    }
    return RedirectResponse(url=f"{MICROSOFT_AUTH_URL}?{urlencode(params)}")

@router.get("/microsoft/callback", response_class=RedirectResponse)
async def microsoft_callback(code: str, db: AsyncSession = Depends(get_db)):
    if not settings.MICROSOFT_CLIENT_ID:
        return error_html_response("Microsoft OAuth not configured", "Configuration Error", 501)

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
            return error_html_response("Failed to exchange Microsoft code", "Authentication Failed", 400)

        token_data = token_resp.json()
        userinfo_resp = await client.get(MICROSOFT_USERINFO_URL, headers={"Authorization": f"Bearer {token_data['access_token']}"})
        if userinfo_resp.status_code != 200:
            return error_html_response("Failed to fetch Microsoft user info", "Authentication Failed", 400)

        userinfo = userinfo_resp.json()

    email = userinfo.get("mail") or userinfo.get("userPrincipalName")
    name = userinfo.get("displayName") or (email.split("@")[0] if email else None)

    if not email:
        return error_html_response("Microsoft account has no email", "Authentication Failed", 400)

    user_ops = UserOperations(db)
    user = await user_ops.get_user_by_email(email)

    if not user:
        username = name.replace(" ", "_").lower() if name else email.split("@")[0].lower()
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

    access_token = await create_access_token(data={"sub": user.username})
    frontend_url = settings.DOMAIN.rstrip('/')
    redirect_url = (
        f"{frontend_url}"
        f"?token={access_token}"
        f"&username={quote(user.username)}"
        f"&email={quote(user.email)}"
        f"&role={user.role}"
    )
    return RedirectResponse(url=redirect_url)