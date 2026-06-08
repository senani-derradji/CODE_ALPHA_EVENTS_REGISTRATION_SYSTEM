"""
Tests for /auth/* endpoints:
  - registration → activation → login flow
  - password reset
  - token validation / expiry
  - inactive-user blocking
  - input validation
"""

import pytest
from httpx import AsyncClient


# ─────────────────────────── Registration ────────────────────────────────────

class TestUserRegistration:
    async def test_register_success(self, client: AsyncClient):
        resp = await client.post("/users/register", json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "Secure123",
        })
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "password" not in data  # never leak hash

    async def test_register_duplicate_username(self, client: AsyncClient, regular_user: dict):
        resp = await client.post("/users/register", json={
            "username": regular_user["username"],
            "email": "different@example.com",
            "password": "Secure123",
        })
        assert resp.status_code == 400
        assert "username" in resp.json()["detail"].lower() or "taken" in resp.json()["detail"].lower()

    async def test_register_duplicate_email(self, client: AsyncClient, regular_user: dict):
        resp = await client.post("/users/register", json={
            "username": "differentname",
            "email": regular_user["email"],
            "password": "Secure123",
        })
        assert resp.status_code == 400
        assert "email" in resp.json()["detail"].lower() or "registered" in resp.json()["detail"].lower()

    async def test_register_weak_password_no_uppercase(self, client: AsyncClient):
        resp = await client.post("/users/register", json={
            "username": "weakpassuser",
            "email": "weak@example.com",
            "password": "alllowercase1",
        })
        assert resp.status_code == 422

    async def test_register_weak_password_no_digit(self, client: AsyncClient):
        resp = await client.post("/users/register", json={
            "username": "weakpassuser2",
            "email": "weak2@example.com",
            "password": "NoDigitsHere",
        })
        assert resp.status_code == 422

    async def test_register_weak_password_too_short(self, client: AsyncClient):
        resp = await client.post("/users/register", json={
            "username": "shortpassuser",
            "email": "short@example.com",
            "password": "Ab1",
        })
        assert resp.status_code == 422

    async def test_register_invalid_email(self, client: AsyncClient):
        resp = await client.post("/users/register", json={
            "username": "bademailuser",
            "email": "not-an-email",
            "password": "Secure123",
        })
        assert resp.status_code == 422

    async def test_register_username_too_short(self, client: AsyncClient):
        resp = await client.post("/users/register", json={
            "username": "ab",
            "email": "shortname@example.com",
            "password": "Secure123",
        })
        assert resp.status_code == 422

    async def test_register_username_invalid_chars(self, client: AsyncClient):
        resp = await client.post("/users/register", json={
            "username": "bad user!",
            "email": "badchar@example.com",
            "password": "Secure123",
        })
        assert resp.status_code == 422


# ─────────────────────────── Login ───────────────────────────────────────────

class TestLogin:
    async def test_login_success(self, client: AsyncClient, regular_user: dict):
        resp = await client.post(
            "/auth/login",
            data={"username": regular_user["username"], "password": regular_user["password"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["username"] == regular_user["username"]

    async def test_login_wrong_password(self, client: AsyncClient, regular_user: dict):
        resp = await client.post(
            "/auth/login",
            data={"username": regular_user["username"], "password": "WrongPass99"},
        )
        assert resp.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        resp = await client.post(
            "/auth/login",
            data={"username": "ghost_user", "password": "AnyPass123"},
        )
        assert resp.status_code == 401

    async def test_login_inactive_user(self, client: AsyncClient):
        """User who has not activated their account must be rejected."""
        await client.post("/users/register", json={
            "username": "inactiveuser",
            "email": "inactive@example.com",
            "password": "Secure123",
        })
        # Do NOT activate → is_active stays 0
        resp = await client.post(
            "/auth/login",
            data={"username": "inactiveuser", "password": "Secure123"},
        )
        assert resp.status_code == 401
        assert "not active" in resp.json()["detail"].lower() or "activate" in resp.json()["detail"].lower()

    async def test_login_returns_role(self, client: AsyncClient, regular_user: dict):
        resp = await client.post(
            "/auth/login",
            data={"username": regular_user["username"], "password": regular_user["password"]},
        )
        assert resp.status_code == 200
        assert "role" in resp.json()


# ─────────────────────────── Protected /auth/me ──────────────────────────────

class TestAuthMe:
    async def test_me_authenticated(self, client: AsyncClient, regular_user_token: str):
        resp = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {regular_user_token}"},
        )
        assert resp.status_code == 200

    async def test_me_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/auth/me")
        assert resp.status_code == 401

    async def test_me_invalid_token(self, client: AsyncClient):
        resp = await client.get(
            "/auth/me",
            headers={"Authorization": "Bearer totally.invalid.token"},
        )
        assert resp.status_code == 401


# ─────────────────────────── Token Validation Helpers ────────────────────────

class TestTokenHelpers:
    async def test_activation_token_round_trip(self):
        from app.utils.validate_user_token import create_activation_token, validate_activation_token

        token = await create_activation_token(user_id=42)
        result = await validate_activation_token(token)
        assert result["valid"] is True
        assert result["user_id"] == 42
        assert result["expired"] is False

    async def test_activation_token_tampered(self):
        from app.utils.validate_user_token import create_activation_token, validate_activation_token

        token = await create_activation_token(user_id=42)
        # Flip last character to corrupt the signature
        tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
        result = await validate_activation_token(tampered)
        assert result["valid"] is False

    async def test_activation_token_garbage(self):
        from app.utils.validate_user_token import validate_activation_token

        result = await validate_activation_token("not.a.valid.token")
        assert result["valid"] is False

    async def test_reset_token_round_trip(self):
        from app.utils.validate_user_token import create_reset_password_token, validate_reset_password_token

        token = await create_reset_password_token(user_id=7)
        result = await validate_reset_password_token(token)
        assert result["valid"] is True
        assert result["user_id"] == 7

    async def test_reset_token_wrong_secret(self):
        """Token signed with a different secret must be rejected."""
        import base64, hmac, hashlib, time, secrets

        user_id = 99
        expires = int(time.time()) + 900
        rp = secrets.token_urlsafe(16)
        payload = f"{user_id}~{expires}~{rp}"
        sig = hmac.new(b"wrong-secret", payload.encode(), hashlib.sha256).hexdigest()
        raw = f"{payload}~{sig}"
        bad_token = base64.urlsafe_b64encode(raw.encode()).decode()

        from app.utils.validate_user_token import validate_reset_password_token
        result = await validate_reset_password_token(bad_token)
        assert result["valid"] is False


# ─────────────────────────── JWT Security ────────────────────────────────────

class TestJWTSecurity:
    async def test_create_and_verify_token(self):
        from app.security.jwt import create_access_token, verify_token
        from fastapi import HTTPException

        token = await create_access_token({"sub": "alice"})
        exc = HTTPException(status_code=401, detail="bad")
        username = await verify_token(token, exc)
        assert username == "alice"

    async def test_verify_expired_token(self):
        from datetime import timedelta
        from app.security.jwt import create_access_token, verify_token
        from fastapi import HTTPException

        token = await create_access_token({"sub": "alice"}, expires_delta=timedelta(seconds=-1))
        exc = HTTPException(status_code=401, detail="bad")
        with pytest.raises(HTTPException) as exc_info:
            await verify_token(token, exc)
        assert exc_info.value.status_code == 401

    async def test_verify_invalid_token(self):
        from app.security.jwt import verify_token
        from fastapi import HTTPException

        exc = HTTPException(status_code=401, detail="bad")
        with pytest.raises(HTTPException):
            await verify_token("garbage.token.data", exc)

    async def test_token_missing_sub(self):
        from app.security.jwt import create_access_token, verify_token
        from fastapi import HTTPException

        # token with no "sub" claim
        token = await create_access_token({"data": "no-sub"})
        exc = HTTPException(status_code=401, detail="bad")
        with pytest.raises(HTTPException):
            await verify_token(token, exc)


# ─────────────────────────── Password Hashing ────────────────────────────────

class TestPasswordHashing:
    async def test_hash_is_not_plaintext(self):
        from app.security.hash import create_password_hash

        h = await create_password_hash("MySecret1")
        assert h != "MySecret1"
        assert len(h) > 20

    async def test_verify_correct_password(self):
        from app.security.hash import create_password_hash, verify_password

        h = await create_password_hash("MySecret1")
        assert await verify_password("MySecret1", h) is True

    async def test_verify_wrong_password(self):
        from app.security.hash import create_password_hash, verify_password

        h = await create_password_hash("MySecret1")
        assert await verify_password("WrongPass9", h) is False

    async def test_two_hashes_of_same_password_differ(self):
        """Argon2 salts each hash — identical plaintexts must never produce identical hashes."""
        from app.security.hash import create_password_hash

        h1 = await create_password_hash("SamePass1")
        h2 = await create_password_hash("SamePass1")
        assert h1 != h2
