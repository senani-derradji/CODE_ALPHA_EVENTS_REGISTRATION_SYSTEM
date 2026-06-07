from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = " sqlite+aiosqlite:///./ACCESS.db"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 72

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str

    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    MICROSOFT_REDIRECT_URI: str
    MICROSOFT_TENANT_ID: str

    FRONTEND_URL: str

    RATE_LIMIT_AUTH: int = 10
    RATE_LIMIT_API: int = 100

    REDIS_URL: Optional[str] = None

    admin_username: str
    admin_email : str
    admin_password: str

    SENDER_EMAIL: str
    EMAIL_APP_PASSWORD: str

    TOKEN_VALIDATION_SECRET: str

    DOMAIN: str


    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_not_be_empty(cls, v: str) -> str:
        if not v or len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v


settings = Settings()
