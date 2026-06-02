import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def org_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def user_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def _register(client, username="authuser", email="auth@test.com", password="Secure123"):
    await client.post("/users/", json={"username": username, "email": email, "password": password})


@pytest.mark.asyncio
async def test_login_success(client):
    await _register(client)
    resp = await client.post("/auth/login", data={"username": "authuser", "password": "Secure123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await _register(client)
    resp = await client.post("/auth/login", data={"username": "authuser", "password": "WrongPass1"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_user(client):
    resp = await client.post("/auth/login", data={"username": "ghost", "password": "Secure123"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_endpoint(client):
    await _register(client)
    login_resp = await client.post("/auth/login", data={"username": "authuser", "password": "Secure123"})
    token = login_resp.json()["access_token"]
    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "authuser"


@pytest.mark.asyncio
async def test_me_without_token(client):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401