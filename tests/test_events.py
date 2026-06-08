"""
Tests for /events/* endpoints:
  - CRUD (create, read, update, delete)
  - Authorization: only org/admin may create or mutate
  - Validation: time ordering, field lengths, attendee bounds
  - Capacity & registration counting
"""

import pytest
from httpx import AsyncClient


VALID_EVENT = {
    "title": "Sample Event",
    "description": "A well-described event for testing purposes.",
    "start_time": "2025-10-01T09:00:00",
    "end_time": "2025-10-01T17:00:00",
    "location": "Test Venue",
    "max_attendees": 50,
}


# ─────────────────────────── Create Event ────────────────────────────────────

class TestCreateEvent:
    async def test_org_can_create_event(self, client: AsyncClient, org_user_token: str):
        resp = await client.post(
            "/events/create/",
            json={**VALID_EVENT, "title": "Org Created Event"},
            headers={"Authorization": f"Bearer {org_user_token}"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Org Created Event"
        assert "id" in data

    async def test_admin_can_create_event(self, client: AsyncClient, admin_token: str):
        resp = await client.post(
            "/events/create/",
            json={**VALID_EVENT, "title": "Admin Created Event"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 201

    async def test_regular_user_cannot_create_event(self, client: AsyncClient, regular_user_token: str):
        resp = await client.post(
            "/events/create/",
            json={**VALID_EVENT, "title": "User Should Fail"},
            headers={"Authorization": f"Bearer {regular_user_token}"},
        )
        assert resp.status_code == 403

    async def test_unauthenticated_cannot_create_event(self, client: AsyncClient):
        resp = await client.post("/events/create/", json=VALID_EVENT)
        assert resp.status_code == 401

    async def test_duplicate_title_rejected(self, client: AsyncClient, org_user_token: str, sample_event: dict):
        resp = await client.post(
            "/events/create/",
            json={**VALID_EVENT, "title": sample_event["title"]},
            headers={"Authorization": f"Bearer {org_user_token}"},
        )
        assert resp.status_code == 400
        assert "already exists" in resp.json()["detail"].lower()

    async def test_end_before_start_rejected(self, client: AsyncClient, org_user_token: str):
        bad_event = {
            **VALID_EVENT,
            "title": "Reversed Times",
            "start_time": "2025-10-01T18:00:00",
            "end_time": "2025-10-01T09:00:00",
        }
        resp = await client.post(
            "/events/create/",
            json=bad_event,
            headers={"Authorization": f"Bearer {org_user_token}"},
        )
        assert resp.status_code == 422

    async def test_max_attendees_zero_rejected(self, client: AsyncClient, org_user_token: str):
        resp = await client.post(
            "/events/create/",
            json={**VALID_EVENT, "title": "Zero Attendees", "max_attendees": 0},
            headers={"Authorization": f"Bearer {org_user_token}"},
        )
        assert resp.status_code == 422

    async def test_title_too_short_rejected(self, client: AsyncClient, org_user_token: str):
        resp = await client.post(
            "/events/create/",
            json={**VALID_EVENT, "title": "Hi"},
            headers={"Authorization": f"Bearer {org_user_token}"},
        )
        assert resp.status_code == 422

    async def test_description_too_short_rejected(self, client: AsyncClient, org_user_token: str):
        resp = await client.post(
            "/events/create/",
            json={**VALID_EVENT, "title": "Good Title", "description": "Short"},
            headers={"Authorization": f"Bearer {org_user_token}"},
        )
        assert resp.status_code == 422


# ─────────────────────────── Read Events ─────────────────────────────────────

class TestReadEvents:
    async def test_list_events_public(self, client: AsyncClient, sample_event: dict):
        resp = await client.get("/events/get_events/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        titles = [e["title"] for e in resp.json()]
        assert sample_event["title"] in titles

    async def test_get_event_by_id(self, client: AsyncClient, sample_event: dict):
        event_id = sample_event["id"]
        resp = await client.get(f"/events/get_event/{event_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == event_id

    async def test_get_nonexistent_event(self, client: AsyncClient):
        resp = await client.get("/events/get_event/999999")
        assert resp.status_code == 404

    async def test_list_events_pagination(self, client: AsyncClient):
        resp = await client.get("/events/get_events/?skip=0&limit=2")
        assert resp.status_code == 200
        assert len(resp.json()) <= 2

    async def test_count_events_authenticated(self, client: AsyncClient, regular_user_token: str, sample_event: dict):
        resp = await client.get(
            "/events/count_events/",
            headers={"Authorization": f"Bearer {regular_user_token}"},
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), int)
        assert resp.json() >= 1

    async def test_count_events_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/events/count_events/")
        assert resp.status_code == 401


# ─────────────────────────── Update Event ────────────────────────────────────

class TestUpdateEvent:
    async def test_org_can_update_own_event(self, client: AsyncClient, org_user_token: str, sample_event: dict):
        resp = await client.put(
            f"/events/update_event/{sample_event['id']}",
            json={"location": "New Location Updated"},
            headers={"Authorization": f"Bearer {org_user_token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["location"] == "New Location Updated"

    async def test_admin_can_update_event(self, client: AsyncClient, admin_token: str, sample_event: dict):
        resp = await client.put(
            f"/events/update_event/{sample_event['id']}",
            json={"max_attendees": 200},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200

    async def test_regular_user_cannot_update_event(self, client: AsyncClient, regular_user_token: str, sample_event: dict):
        resp = await client.put(
            f"/events/update_event/{sample_event['id']}",
            json={"location": "Hacker Location"},
            headers={"Authorization": f"Bearer {regular_user_token}"},
        )
        assert resp.status_code == 403

    async def test_update_nonexistent_event(self, client: AsyncClient, org_user_token: str):
        resp = await client.put(
            "/events/update_event/999999",
            json={"location": "Nowhere"},
            headers={"Authorization": f"Bearer {org_user_token}"},
        )
        assert resp.status_code == 404


# ─────────────────────────── Delete Event ────────────────────────────────────

class TestDeleteEvent:
    async def test_admin_can_delete_event(self, client: AsyncClient, admin_token: str, org_user_token: str):
        # Create a fresh event just to delete
        resp = await client.post(
            "/events/create/",
            json={**VALID_EVENT, "title": "Event To Delete"},
            headers={"Authorization": f"Bearer {org_user_token}"},
        )
        event_id = resp.json()["id"]
        del_resp = await client.delete(
            f"/events/delete_event/{event_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert del_resp.status_code == 204

    async def test_regular_user_cannot_delete_event(self, client: AsyncClient, regular_user_token: str, sample_event: dict):
        resp = await client.delete(
            f"/events/delete_event/{sample_event['id']}",
            headers={"Authorization": f"Bearer {regular_user_token}"},
        )
        assert resp.status_code == 403

    async def test_delete_nonexistent_event(self, client: AsyncClient, admin_token: str):
        resp = await client.delete(
            "/events/delete_event/999999",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 404


# ─────────────────────────── Check user in event ─────────────────────────────

class TestCheckUserInEvent:
    async def test_unregistered_user_returns_404(self, client: AsyncClient, regular_user: dict, sample_event: dict):
        resp = await client.get(
            f"/events/check_user_in_event/{regular_user['email']}/{sample_event['id']}"
        )
        assert resp.status_code == 404
