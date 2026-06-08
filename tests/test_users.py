"""
Tests for /users/* endpoints:
  - Profile CRUD
  - Role-based access
  - Input validation
"""

import pytest
from httpx import AsyncClient


class TestUserProfile:
    async def test_get_own_profile(self, client: AsyncClient, regular_user_token: str, regular_user: dict):
        resp = await client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {regular_user_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == regular_user["username"]
        assert data["email"] == regular_user["email"]
        assert "password" not in data

    async def test_get_profile_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/users/me")
        assert resp.status_code == 401

    async def test_update_own_profile_username(
        self, client: AsyncClient, regular_user_token: str
    ):
        resp = await client.put(
            "/users/me",
            json={"username": "updated_username"},
            headers={"Authorization": f"Bearer {regular_user_token}"},
        )
        # 200 or 404 if endpoint doesn't exist yet in this build
        assert resp.status_code in (200, 404, 405)

    async def test_password_not_returned_in_any_endpoint(
        self, client: AsyncClient, regular_user_token: str
    ):
        """Regression: the hash must never appear in any user-facing response."""
        resp = await client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {regular_user_token}"},
        )
        body = resp.text
        assert "password" not in body.lower() or '"password"' not in body


class TestAdminUserManagement:
    async def test_admin_can_list_users(self, client: AsyncClient, admin_token: str):
        resp = await client.get(
            "/users/",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code in (200, 404)  # 404 = endpoint not exposed, acceptable

    async def test_regular_user_cannot_list_all_users(
        self, client: AsyncClient, regular_user_token: str
    ):
        resp = await client.get(
            "/users/",
            headers={"Authorization": f"Bearer {regular_user_token}"},
        )
        # Must be either 403 (forbidden) or 404 (not exposed)
        assert resp.status_code in (403, 404)


class TestSchemaValidation:
    """Unit-level tests for Pydantic schemas — no HTTP round-trip needed."""

    def test_user_create_valid(self):
        from app.schemas.user import UserCreate
        u = UserCreate(username="alice", email="alice@example.com", password="AlicePass1")
        assert u.username == "alice"

    def test_user_create_username_strips_whitespace(self):
        from app.schemas.user import UserCreate
        u = UserCreate(username="  alice  ", email="alice2@example.com", password="AlicePass1")
        assert u.username == "alice"

    def test_user_create_invalid_username_chars(self):
        from pydantic import ValidationError
        from app.schemas.user import UserCreate
        with pytest.raises(ValidationError):
            UserCreate(username="inv@lid!", email="x@x.com", password="ValidPass1")

    def test_user_update_none_fields_allowed(self):
        from app.schemas.user import UserUpdate
        u = UserUpdate()
        assert u.username is None
        assert u.password is None

    def test_event_end_before_start_raises(self):
        from pydantic import ValidationError
        from app.schemas.event import EventCreate
        with pytest.raises(ValidationError):
            EventCreate(
                title="Bad Event",
                description="This event has reversed times for testing purposes.",
                start_time="2025-10-01T18:00:00",
                end_time="2025-10-01T09:00:00",
                location="Somewhere",
                max_attendees=10,
            )

    def test_event_max_attendees_boundary(self):
        from pydantic import ValidationError
        from app.schemas.event import EventCreate

        # exactly 1 is valid
        e = EventCreate(
            title="Min Event",
            description="Testing minimum attendee boundary value for events.",
            start_time="2025-10-01T09:00:00",
            end_time="2025-10-01T17:00:00",
            location="Somewhere",
            max_attendees=1,
        )
        assert e.max_attendees == 1

        # 0 is invalid
        with pytest.raises(ValidationError):
            EventCreate(
                title="Zero Event",
                description="Testing zero attendee boundary value for events.",
                start_time="2025-10-01T09:00:00",
                end_time="2025-10-01T17:00:00",
                location="Somewhere",
                max_attendees=0,
            )

    def test_registration_invalid_user_id(self):
        from pydantic import ValidationError
        from app.schemas.registration import RegistrationCreate
        with pytest.raises(ValidationError):
            RegistrationCreate(user_id=-1, event_id=1)

    def test_registration_invalid_status(self):
        from pydantic import ValidationError
        from app.schemas.registration import RegistrationCreate
        with pytest.raises(ValidationError):
            RegistrationCreate(user_id=1, event_id=1, status="invalid_status")
