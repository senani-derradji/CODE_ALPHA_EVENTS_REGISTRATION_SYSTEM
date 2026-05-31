import pytest


def _register(client, username="authuser", email="auth@test.com", password="Secure123"):
    client.post("/users/create/", json={"username": username, "email": email, "password": password})


def test_login_success(client):
    _register(client)
    resp = client.post("/auth/login", data={"username": "authuser", "password": "Secure123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    _register(client)
    resp = client.post("/auth/login", data={"username": "authuser", "password": "WrongPass1"})
    assert resp.status_code == 401


def test_login_unknown_user(client):
    resp = client.post("/auth/login", data={"username": "ghost", "password": "Secure123"})
    assert resp.status_code == 401


def test_me_endpoint(client):
    _register(client)
    token = client.post("/auth/login", data={"username": "authuser", "password": "Secure123"}).json()["access_token"]
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "authuser"


def test_me_without_token(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401
