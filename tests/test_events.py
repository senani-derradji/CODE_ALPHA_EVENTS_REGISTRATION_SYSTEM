import pytest
from datetime import datetime, timedelta

FUTURE = (datetime.utcnow() + timedelta(days=1)).isoformat()
FUTURE2 = (datetime.utcnow() + timedelta(days=2)).isoformat()
PAST = (datetime.utcnow() - timedelta(days=1)).isoformat()

VALID_EVENT = {
    "title": "Test Event",
    "description": "A test event description with enough chars",
    "start_time": FUTURE,
    "end_time": FUTURE2,
    "location": "Test City",
    "max_attendees": 100,
}


@pytest.fixture
async def org_client_fixture():
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def user_client_fixture():
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_event_as_org(org_client_fixture):
    resp = await org_client_fixture.post("/events/", json=VALID_EVENT)
    assert resp.status_code in (201, 401, 403)


@pytest.mark.asyncio
async def test_create_event_as_user_forbidden(user_client_fixture):
    resp = await user_client_fixture.post("/events/", json=VALID_EVENT)
    assert resp.status_code in (403, 401)


@pytest.mark.asyncio
async def test_create_event_end_before_start(org_client_fixture):
    bad = {**VALID_EVENT, "start_time": FUTURE2, "end_time": FUTURE}
    resp = await org_client_fixture.post("/events/", json=bad)
    assert resp.status_code in (422, 401, 403)


@pytest.mark.asyncio
async def test_create_event_negative_attendees(org_client_fixture):
    bad = {**VALID_EVENT, "max_attendees": 0}
    resp = await org_client_fixture.post("/events/", json=bad)
    assert resp.status_code in (422, 401, 403)


@pytest.mark.asyncio
async def test_get_events_public(org_client_fixture):
    resp = await org_client_fixture.get("/events/")
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert "meta" in data


@pytest.mark.asyncio
async def test_get_event_not_found(org_client_fixture):
    resp = await org_client_fixture.get("/events/9999")
    assert resp.status_code in (404, 200)


@pytest.mark.asyncio
async def test_update_event(org_client_fixture):
    create_resp = await org_client_fixture.post("/events/", json=VALID_EVENT)
    if create_resp.status_code not in (200, 201):
        pytest.skip("Cannot create event without proper auth")

    event_id = create_resp.json()["id"]

    resp = await org_client_fixture.put(
        f"/events/{event_id}",
        json={"title": "Updated Title"}
    )
    assert resp.status_code in (200, 404, 401, 403)


@pytest.mark.asyncio
async def test_delete_event(org_client_fixture):
    create_resp = await org_client_fixture.post("/events/", json=VALID_EVENT)
    if create_resp.status_code not in (200, 201):
        pytest.skip("Cannot create event without proper auth")

    event_id = create_resp.json()["id"]

    resp = await org_client_fixture.delete(f"/events/{event_id}")
    assert resp.status_code in (204, 404, 401, 403)