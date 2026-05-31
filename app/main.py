from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middlewares.rate_limit import RateLimitMiddleware
from app.middlewares.security_headers import SecurityHeadersMiddleware
from app.routers.users import router as user_router
from app.routers.events import router as router_events
from app.routers.registrations import router as router_registrations
from app.routers.auth import router as router_auth
from app.routers.admin import router as router_admin
from app.utils.create_super_user import create_user
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Event Management API", version="1.0.0")

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.RATE_LIMIT_API,
    auth_requests_per_minute=settings.RATE_LIMIT_AUTH,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    # Run alembic migrations on startup (safe for SQLite dev; use CLI in prod)
    from alembic.config import Config
    from alembic import command
    import os

    alembic_cfg = Config(os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic.ini"))
    try:
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations applied successfully")
    except Exception as e:
        logger.warning(f"Alembic migration skipped (may need manual run): {e}")
        # Fallback for dev: create tables directly
        from app.core.database import engine, Base
        from app.models.event import Event  # noqa
        from app.models.user import User  # noqa
        from app.models.registration import Registration  # noqa
        Base.metadata.create_all(bind=engine)

    create_user()


@app.get("/")
async def root():
    return {"message": "Event Management API", "version": "1.0.0"}


app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(router_events, prefix="/events", tags=["events"])
app.include_router(router_registrations, prefix="/registrations", tags=["registrations"])
app.include_router(router_auth, prefix="/auth", tags=["auth"])
app.include_router(router_admin, prefix="/admin", tags=["admin"])
