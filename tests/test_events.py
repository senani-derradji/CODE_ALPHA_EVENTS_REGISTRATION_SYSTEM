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


def test_create_event_as_org(client, org_token):
    resp = client.post("/events/create/", json=VALID_EVENT, headers={"Authorization": f"Bearer {org_token}"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test Event"
    assert data["organizer_id"] is not None  # organizer_id correctly stored


def test_create_event_as_user_forbidden(client, user_token):
    resp = client.post("/events/create/", json=VALID_EVENT, headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 403


def test_create_event_end_before_start(client, org_token):
    bad = {**VALID_EVENT, "start_time": FUTURE2, "end_time": FUTURE}
    resp = client.post("/events/create/", json=bad, headers={"Authorization": f"Bearer {org_token}"})
    assert resp.status_code == 422


def test_create_event_negative_attendees(client, org_token):
    bad = {**VALID_EVENT, "max_attendees": 0}
    resp = client.post("/events/create/", json=bad, headers={"Authorization": f"Bearer {org_token}"})
    assert resp.status_code == 422


def test_get_events_public(client):
    resp = client.get("/events/get_events/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_event_not_found(client):
    resp = client.get("/events/get_event/9999")
    assert resp.status_code == 404


def test_update_event(client, org_token):
    create_resp = client.post("/events/create/", json=VALID_EVENT, headers={"Authorization": f"Bearer {org_token}"})
    event_id = create_resp.json()["id"]

    resp = client.put(
        f"/events/update_event/{event_id}",
        json={"title": "Updated Title"},
        headers={"Authorization": f"Bearer {org_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"


def test_delete_event(client, org_token):
    create_resp = client.post("/events/create/", json=VALID_EVENT, headers={"Authorization": f"Bearer {org_token}"})
    event_id = create_resp.json()["id"]

    resp = client.delete(f"/events/delete_event/{event_id}", headers={"Authorization": f"Bearer {org_token}"})
    assert resp.status_code == 204
