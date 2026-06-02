import pytest
from httpx import AsyncClient

from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(
        app=app,
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def client_user():
    async with AsyncClient(
        app=app,
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def admin_client():
    async with AsyncClient(
        app=app,
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def org_client():
    async with AsyncClient(
        app=app,
        base_url="http://test"
    ) as ac:
        yield ac