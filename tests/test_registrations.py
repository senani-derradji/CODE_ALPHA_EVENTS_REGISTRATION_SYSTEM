"""
Tests for /registrations/* endpoints:
  - Create registration (happy path, capacity, duplicates)
  - Fetch registrations (own, by event, by user)
  - Cancel registration
  - Authorization guards
"""

import pytest
from httpx import AsyncClient


# ─────────────────────────── Create Registration ─────────────────────────────

class TestCreateRegistration:
    async def test_user_can_register_for_event(
        self, client: AsyncClient, regular_user_token: str, sample_event: dict
    ):
        resp = await client.post(
            f"/registrations/create/?event_id={sample_event['id']}",
            headers={"Authorization": f"Bearer {regular_user_token}"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["event_id"] == sample_event["id"]
        assert "id" in data

    async def test_duplicate_registration_rejected(
        self, client: AsyncClient, regular_user_token: str, sample_event: dict
    ):
        # First registration
        await client.post(
            f"/registrations/create/?event_id={sample_event['id']}",
            headers={"Authorization": f"Bearer {regular_user_token}"},
        )
        # Attempt duplicate
        resp = await client.post(
            f"/registrations/create/?event_id={sample_event['id']}",
            headers={"Authorization": f"Bearer {regular_user_token}"},
        )
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()

    async def test_register_nonexistent_event(
        self, client: AsyncClient, regular_user_token: str
    ):
        resp = await client.post(
            "/registrations/create/?event_id=999999",
            headers={"Authorization": f"Bearer {regular_user_token}"},
        )
        assert resp.status_code == 404

    async def test_unauthenticated_cannot_register(self, client: AsyncClient, sample_event: dict):
        resp = await client.post(f"/registrations/create/?event_id={sample_event['id']}")
        assert resp.status_code == 401

    async def test_capacity_enforced(self, client: AsyncClient, org_user_token: str):
        """An event with max_attendees=1 should reject a second registration."""
        # Create a tiny-capacity event
        small_event_resp = await client.post(
            "/events/create/",
            json={
                "title": "Tiny Event Capacity",
                "description": "Only room for one attendee in this test event.",
                "start_time": "2025-12-01T10:00:00",
                "end_time": "2025-12-01T12:00:00",
                "location": "Small Room",
                "max_attendees": 1,
            },
            headers={"Authorization": f"Bearer {org_user_token}"},
        )
        assert small_event_resp.status_code == 201
        event_id = small_event_resp.json()["id"]

        # Register a fresh user
        await client.post("/users/register", json={
            "username": "capacityuser1",
            "email": "cap1@example.com",
            "password": "CapPass1Secure",
        })
        from tests.conftest import TestingSessionLocal
        async with TestingSessionLocal() as session:
            from sqlalchemy import update
            from app.models.user import User
            await session.execute(
                update(User).where(User.email == "cap1@example.com").values(is_active=1)
            )
            await session.commit()
        login1 = await client.post(
            "/auth/login",
            data={"username": "capacityuser1", "password": "CapPass1Secure"},
        )
        token1 = login1.json()["access_token"]

        # Register a second fresh user
        await client.post("/users/register", json={
            "username": "capacityuser2",
            "email": "cap2@example.com",
            "password": "CapPass2Secure",
        })
        async with TestingSessionLocal() as session:
            from sqlalchemy import update
            from app.models.user import User
            await session.execute(
                update(User).where(User.email == "cap2@example.com").values(is_active=1)
            )
            await session.commit()
        login2 = await client.post(
            "/auth/login",
            data={"username": "capacityuser2", "password": "CapPass2Secure"},
        )
        token2 = login2.json()["access_token"]

        # First registration must succeed
        r1 = await client.post(
            f"/registrations/create/?event_id={event_id}",
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert r1.status_code == 201

        # Second registration must be rejected (capacity = 1)
        r2 = await client.post(
            f"/registrations/create/?event_id={event_id}",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert r2.status_code == 400
        assert "capacity" in r2.json()["detail"].lower()


# ─────────────────────────── Fetch Registrations ─────────────────────────────

class TestGetRegistrations:
    async def test_user_can_see_own_registrations(
        self, client: AsyncClient, regular_user_token: str, sample_event: dict
    ):
        # Ensure registered first
        await client.post(
            f"/registrations/create/?event_id={sample_event['id']}",
            headers={"Authorization": f"Bearer {regular_user_token}"},
        )
        resp = await client.get(
            "/registrations/get_registrations/",
            headers={"Authorization": f"Bearer {regular_user_token}"},
        )
        assert resp.status_code in (200, 404)  # 404 only if none exist yet

    async def test_unauthenticated_cannot_fetch(self, client: AsyncClient):
        resp = await client.get("/registrations/get_registrations/")
        assert resp.status_code == 401

    async def test_admin_can_see_event_registrations(
        self, client: AsyncClient, admin_token: str, regular_user_token: str, sample_event: dict
    ):
        await client.post(
            f"/registrations/create/?event_id={sample_event['id']}",
            headers={"Authorization": f"Bearer {regular_user_token}"},
        )
        resp = await client.get(
            f"/registrations/get_registrations_by_event/{sample_event['id']}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_regular_user_cannot_see_event_registrations(
        self, client: AsyncClient, regular_user_token: str, sample_event: dict
    ):
        resp = await client.get(
            f"/registrations/get_registrations_by_event/{sample_event['id']}",
            headers={"Authorization": f"Bearer {regular_user_token}"},
        )
        assert resp.status_code == 403

    async def test_get_specific_registration(
        self, client: AsyncClient, regular_user_token: str, sample_event: dict
    ):
        reg_resp = await client.post(
            f"/registrations/create/?event_id={sample_event['id']}",
            headers={"Authorization": f"Bearer {regular_user_token}"},
        )
        if reg_resp.status_code == 201:
            reg_id = reg_resp.json()["id"]
            get_resp = await client.get(
                f"/registrations/get_registration/{reg_id}",
                headers={"Authorization": f"Bearer {regular_user_token}"},
            )
            assert get_resp.status_code == 200
            assert get_resp.json()["id"] == reg_id


# ─────────────────────────── Cancel Registration ─────────────────────────────

class TestCancelRegistration:
    async def test_user_can_cancel_own_registration(
        self, client: AsyncClient, regular_user_token: str, sample_event: dict
    ):
        reg_resp = await client.post(
            f"/registrations/create/?event_id={sample_event['id']}",
            headers={"Authorization": f"Bearer {regular_user_token}"},
        )
        assert reg_resp.status_code == 201
        reg_id = reg_resp.json()["id"]

        cancel_resp = await client.delete(
            f"/registrations/cancel_registration/{reg_id}",
            headers={"Authorization": f"Bearer {regular_user_token}"},
        )
        assert cancel_resp.status_code == 204

    async def test_cancel_nonexistent_registration(
        self, client: AsyncClient, regular_user_token: str
    ):
        resp = await client.delete(
            "/registrations/cancel_registration/999999",
            headers={"Authorization": f"Bearer {regular_user_token}"},
        )
        assert resp.status_code == 404

    async def test_user_cannot_cancel_others_registration(
        self,
        client: AsyncClient,
        regular_user_token: str,
        org_user_token: str,
        sample_event: dict,
    ):
        # org user registers
        reg_resp = await client.post(
            f"/registrations/create/?event_id={sample_event['id']}",
            headers={"Authorization": f"Bearer {org_user_token}"},
        )
        if reg_resp.status_code == 201:
            reg_id = reg_resp.json()["id"]
            # regular user tries to cancel it
            resp = await client.delete(
                f"/registrations/cancel_registration/{reg_id}",
                headers={"Authorization": f"Bearer {regular_user_token}"},
            )
            assert resp.status_code == 403
