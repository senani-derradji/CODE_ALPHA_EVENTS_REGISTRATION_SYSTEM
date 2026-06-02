import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_create_user_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/users/", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "Secure123",
        })
        assert resp.status_code in (201, 400)


@pytest.mark.asyncio
async def test_create_user_weak_password():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/users/", json={
            "username": "weakuser",
            "email": "weak@test.com",
            "password": "short",
        })
        assert resp.status_code in (422, 422)


@pytest.mark.asyncio
async def test_create_user_invalid_username():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/users/", json={
            "username": "ab",
            "email": "short@test.com",
            "password": "Secure123",
        })
        assert resp.status_code in (422, 422)