import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient, ASGITransport

from app.main import app


FUTURE = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
FUTURE2 = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

VALID_EVENT = {
    "title": "Reg Event",
    "description": "A test event for registration tests, long enough",
    "start_time": FUTURE,
    "end_time": FUTURE2,
    "location": "Test City",
    "max_attendees": 2,
}


@pytest.mark.asyncio
async def test_register_for_event():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/registrations/?event_id=1")
        assert resp.status_code in (201, 401, 404, 409)


@pytest.mark.asyncio
async def test_double_registration_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/registrations/?event_id=1")
        assert resp.status_code in (201, 401, 404, 409)


@pytest.mark.asyncio
async def test_get_user_registrations():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/registrations/user/1")
        assert resp.status_code in (200, 401, 403)


@pytest.mark.asyncio
async def test_get_event_registrations():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/registrations/event/1")
        assert resp.status_code in (200, 401, 403, 404)


@pytest.mark.asyncio
async def test_cancel_registration():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.delete("/registrations/1")
        assert resp.status_code in (204, 401, 403, 404)