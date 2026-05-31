import pytest


def test_create_user_success(client):
    resp = client.post("/users/create/", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "Secure123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "access_token" in data


def test_create_user_duplicate_email(client):
    payload = {"username": "user1", "email": "dup@test.com", "password": "Secure123"}
    client.post("/users/create/", json=payload)
    payload["username"] = "user2"
    resp = client.post("/users/create/", json=payload)
    assert resp.status_code == 400
    assert "Email already registered" in resp.json()["detail"]


def test_create_user_weak_password(client):
    resp = client.post("/users/create/", json={
        "username": "weakuser",
        "email": "weak@test.com",
        "password": "short",
    })
    assert resp.status_code == 422


def test_create_user_invalid_username(client):
    resp = client.post("/users/create/", json={
        "username": "ab",  # too short
        "email": "short@test.com",
        "password": "Secure123",
    })
    assert resp.status_code == 422


def test_get_users_requires_admin(client, user_token):
    resp = client.get("/users/get_users/", headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 403


def test_get_users_as_admin(client, admin_token):
    resp = client.get("/users/get_users/", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_own_profile(client, user_token):
    from app.models.user import User
    from tests.conftest import TestingSessionLocal
    session = TestingSessionLocal()
    user = session.query(User).filter(User.username == "user_test").first()
    user_id = user.id
    session.close()

    resp = client.get(f"/users/get_user/{user_id}", headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "user_test"


def test_cannot_view_other_user_profile(client, user_token, admin_token):
    from app.models.user import User
    from tests.conftest import TestingSessionLocal
    session = TestingSessionLocal()
    admin = session.query(User).filter(User.username == "admin_test").first()
    admin_id = admin.id
    session.close()

    resp = client.get(f"/users/get_user/{admin_id}", headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 403
