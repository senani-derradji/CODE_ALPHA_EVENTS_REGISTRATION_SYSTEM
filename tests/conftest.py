import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def client_user():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def admin_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def org_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def authenticated_client(client):
    response = await client.post(
        "/auth/login",
        data={
            "username": "test@test.com",
            "password": "Password123!"
        },
        follow_redirects=True
    )
    if response.status_code == 200:
        client.headers.update({
            "Authorization": f"Bearer {response.json().get('access_token', '')}"
        })
    yield client