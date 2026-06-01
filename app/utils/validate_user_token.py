import base64
import hashlib
import hmac
import secrets
import time
from app.core.config import settings


SECRET_KEY = settings.TOKEN_VALIDATION_SECRET


async def create_activation_token(user_id: int, expires_in: int = 86400) -> str:

    expires = int(time.time()) + expires_in

    random_part = secrets.token_urlsafe(12)

    payload = f"{user_id}~{expires}~{random_part}"

    signature = hmac.new(
        SECRET_KEY.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    token = f"{payload}~{signature}"

    encoded = base64.urlsafe_b64encode(token.encode()).decode()

    return encoded


async def validate_activation_token(token: str):

    try:
        decoded = base64.urlsafe_b64decode(token.encode()).decode()

        user_id, expires, random_part, received_sig = decoded.split("~")

        payload = f"{user_id}~{expires}~{random_part}"

        expected_sig = hmac.new(
            SECRET_KEY.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(received_sig, expected_sig):
            return {
                "valid": False,
                "user_id": None,
                "expired": False
            }

        if int(expires) < int(time.time()):
            return {
                "valid": False,
                "user_id": int(user_id),
                "expired": True
            }

        return {
            "valid": True,
            "user_id": int(user_id),
            "expired": False
        }

    except Exception:
        return {
            "valid": False,
            "user_id": None,
            "expired": False
        }

async def create_reset_password_token(user_id: int, expires_in: int = 900) -> str:

    expires = int(time.time()) + expires_in
    random_part = secrets.token_urlsafe(16)

    payload = f"{user_id}~{expires}~{random_part}"

    signature = hmac.new(
        SECRET_KEY.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    token = f"{payload}~{signature}"

    return base64.urlsafe_b64encode(token.encode()).decode()



async def validate_reset_password_token(token: str):
    try:
        decoded = base64.urlsafe_b64decode(token.encode()).decode()
        user_id, expires, random_part, received_sig = decoded.split("~")

        payload = f"{user_id}~{expires}~{random_part}"

        expected_sig = hmac.new(
            SECRET_KEY.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(received_sig, expected_sig):
            return {
                "valid": False,
                "user_id": None,
                "expired": False
            }

        if int(expires) < int(time.time()):
            return {
                "valid": False,
                "user_id": int(user_id),
                "expired": True
            }

        return {
            "valid": True,
            "user_id": int(user_id),
            "expired": False
        }

    except Exception:
        return {
            "valid": False,
            "user_id": None,
            "expired": False
        }