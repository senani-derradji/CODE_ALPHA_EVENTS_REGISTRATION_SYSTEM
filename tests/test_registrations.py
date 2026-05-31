import pytest
from datetime import datetime, timezone, timedelta

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


def _create_event(client, org_token):
    resp = client.post("/events/create/", json=VALID_EVENT, headers={"Authorization": f"Bearer {org_token}"})
    return resp.json()["id"]


def _get_user_id(username):
    from app.models.user import User
    from tests.conftest import TestingSessionLocal
    session = TestingSessionLocal()
    user = session.query(User).filter(User.username == username).first()
    uid = user.id
    session.close()
    return uid


def test_register_for_event(client, user_token, org_token):
    event_id = _create_event(client, org_token)
    user_id = _get_user_id("user_test")

    resp = client.post(
        "/registrations/create/",
        json={"user_id": user_id, "event_id": event_id},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["event_id"] == event_id


def test_double_registration_rejected(client, user_token, org_token):
    event_id = _create_event(client, org_token)
    user_id = _get_user_id("user_test")
    payload = {"user_id": user_id, "event_id": event_id}
    headers = {"Authorization": f"Bearer {user_token}"}

    client.post("/registrations/create/", json=payload, headers=headers)
    resp = client.post("/registrations/create/", json=payload, headers=headers)
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"]


def test_capacity_limit(client, org_token):
    event_id = _create_event(client, org_token)

    from app.models.user import User
    from app.security.hash import create_password_hash
    from app.security.jwt import create_access_token
    from tests.conftest import TestingSessionLocal

    session = TestingSessionLocal()
    tokens = []
    for i in range(3):
        u = User(username=f"cap_user_{i}", email=f"cap{i}@test.com",
                 password=create_password_hash("Cap1234!"), role="user")
        session.add(u)
        session.flush()
        tokens.append((u.id, create_access_token(data={"sub": u.username})))
    session.commit()
    session.close()

    statuses = []
    for uid, tok in tokens:
        r = client.post(
            "/registrations/create/",
            json={"user_id": uid, "event_id": event_id},
            headers={"Authorization": f"Bearer {tok}"},
        )
        statuses.append(r.status_code)

    assert statuses.count(201) == 2
    assert statuses.count(400) == 1


def test_user_cannot_register_on_behalf_of_others(client, user_token, org_token):
    """A regular user trying to pass another user's ID should get 403."""
    event_id = _create_event(client, org_token)
    org_id = _get_user_id("org_test")

    resp = client.post(
        "/registrations/create/",
        json={"user_id": org_id, "event_id": event_id},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    # The router checks: if role==user and id != registration.user_id → 403
    assert resp.status_code == 403


def test_get_registrations_by_user(client, user_token, org_token):
    event_id = _create_event(client, org_token)
    user_id = _get_user_id("user_test")

    client.post(
        "/registrations/create/",
        json={"user_id": user_id, "event_id": event_id},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    resp = client.get(
        f"/registrations/get_registrations_by_user/{user_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
