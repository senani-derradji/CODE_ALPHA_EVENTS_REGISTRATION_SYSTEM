from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.core.config import settings
from app.middlewares.rate_limit import RateLimitMiddleware
from app.middlewares.security_headers import SecurityHeadersMiddleware

from app.routers.users import router as user_router
from app.routers.events import router as router_events
from app.routers.registrations import router as router_registrations
from app.routers.auth import router as router_auth
from app.routers.admin import router as router_admin

from app.utils.create_super_user import create_user


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Event Management API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.RATE_LIMIT_API,
    auth_requests_per_minute=settings.RATE_LIMIT_AUTH,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def init_db():
    from app.core.database import Base, engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


from app.background.notification import start_scheduler

@app.on_event("startup")
async def startup():
    await init_db()
    await create_user()
    start_scheduler()


@app.get("/", include_in_schema=False)
async def frontend():
    return FileResponse(
        BASE_DIR / "frontend" / "index.html"
    )



@app.get("/api", tags=["System"])
async def api_info():
    return {
        "name": "Event Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


app.include_router(
    user_router,
    prefix="/users",
    tags=["Users"],
)

app.include_router(
    router_events,
    prefix="/events",
    tags=["Events"],
)

app.include_router(
    router_registrations,
    prefix="/registrations",
    tags=["Registrations"],
)

app.include_router(
    router_auth,
    prefix="/auth",
    tags=["Authentication"],
)

app.include_router(
    router_admin,
    prefix="/admin",
    tags=["Admin"],
)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "event-management-api",
        "version": "1.0.0",
    }