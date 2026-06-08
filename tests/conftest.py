"""
Shared pytest fixtures for the Events Registration System test suite.
Uses an in-memory SQLite database so tests are fully isolated and fast.
"""

import asyncio
import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator

# ── point settings at a test .env BEFORE any app import touches pydantic-settings
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars-long!")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_HOURS", "1")
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")
os.environ.setdefault("DOMAIN", "http://localhost:8000")
os.environ.setdefault("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
os.environ.setdefault("MICROSOFT_REDIRECT_URI", "http://localhost:8000/auth/microsoft/callback")
os.environ.setdefault("MICROSOFT_TENANT_ID", "common")
os.environ.setdefault("RATE_LIMIT_AUTH", "100")
os.environ.setdefault("RATE_LIMIT_API", "1000")
os.environ.setdefault("admin_username", "testadmin")
os.environ.setdefault("admin_email", "admin@test.com")
os.environ.setdefault("admin_password", "Admin@Password123")
os.environ.setdefault("SENDER_EMAIL", "sender@test.com")
os.environ.setdefault("EMAIL_APP_PASSWORD", "test-email-password")
os.environ.setdefault("TOKEN_VALIDATION_SECRET", "test-token-validation-secret-32chars!!")

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app

# ── test database engine (in-memory SQLite) ──────────────────────────────────

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── override the real DB dependency with the test one ────────────────────────

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


# ── create / drop tables around the whole test session ───────────────────────

@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables():
    """Create all tables once per session; drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ── per-test DB session (rolls back after each test) ─────────────────────────

@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


# ── HTTP client ──────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# ── helper fixtures: pre-created users ───────────────────────────────────────

@pytest_asyncio.fixture
async def regular_user(client: AsyncClient) -> dict:
    """Register + return a plain 'user' account (pre-activated via DB)."""
    payload = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "SecurePass1",
    }
    resp = await client.post("/users/register", json=payload)
    assert resp.status_code in (200, 201), resp.text

    # Force-activate: bypass email flow
    async with TestingSessionLocal() as session:
        from sqlalchemy import select, update
        from app.models.user import User
        await session.execute(
            update(User).where(User.email == payload["email"]).values(is_active=1)
        )
        await session.commit()

    return payload


@pytest_asyncio.fixture
async def regular_user_token(client: AsyncClient, regular_user: dict) -> str:
    resp = await client.post(
        "/auth/login",
        data={"username": regular_user["username"], "password": regular_user["password"]},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def org_user(client: AsyncClient) -> dict:
    payload = {
        "username": "orguser",
        "email": "org@example.com",
        "password": "OrgPass1Secure",
    }
    resp = await client.post("/users/register", json=payload)
    assert resp.status_code in (200, 201), resp.text

    async with TestingSessionLocal() as session:
        from sqlalchemy import update
        from app.models.user import User
        await session.execute(
            update(User)
            .where(User.email == payload["email"])
            .values(is_active=1, role="organization")
        )
        await session.commit()

    return payload


@pytest_asyncio.fixture
async def org_user_token(client: AsyncClient, org_user: dict) -> str:
    resp = await client.post(
        "/auth/login",
        data={"username": org_user["username"], "password": org_user["password"]},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def admin_user(client: AsyncClient) -> dict:
    payload = {
        "username": "adminuser",
        "email": "adminuser@example.com",
        "password": "AdminPass1Secure",
    }
    resp = await client.post("/users/register", json=payload)
    assert resp.status_code in (200, 201), resp.text

    async with TestingSessionLocal() as session:
        from sqlalchemy import update
        from app.models.user import User
        await session.execute(
            update(User)
            .where(User.email == payload["email"])
            .values(is_active=1, role="admin")
        )
        await session.commit()

    return payload


@pytest_asyncio.fixture
async def admin_token(client: AsyncClient, admin_user: dict) -> str:
    resp = await client.post(
        "/auth/login",
        data={"username": admin_user["username"], "password": admin_user["password"]},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


# ── helper: create a sample event ────────────────────────────────────────────

@pytest_asyncio.fixture
async def sample_event(client: AsyncClient, org_user_token: str) -> dict:
    payload = {
        "title": "Tech Conference 2025",
        "description": "Annual technology conference with workshops and keynotes.",
        "start_time": "2025-09-01T09:00:00",
        "end_time": "2025-09-01T18:00:00",
        "location": "Algiers Convention Center",
        "max_attendees": 100,
    }
    resp = await client.post(
        "/events/create/",
        json=payload,
        headers={"Authorization": f"Bearer {org_user_token}"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()
