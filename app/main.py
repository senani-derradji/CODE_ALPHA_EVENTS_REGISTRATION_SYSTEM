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
# from app.utils.logger_ import logger


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

async def init_db():
    from app.core.database import Base, engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("startup")
async def startup():
    await init_db()
    await create_user()


@app.get("/")
async def root():
    return {"message": "Event Management API", "version": "1.0.0"}


app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(router_events, prefix="/events", tags=["events"])
app.include_router(router_registrations, prefix="/registrations", tags=["registrations"])
app.include_router(router_auth, prefix="/auth", tags=["auth"])
app.include_router(router_admin, prefix="/admin", tags=["admin"])
