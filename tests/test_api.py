# tests/test_api.py

import pytest
from httpx import AsyncClient


# =====================================================
# AUTH
# =====================================================

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@test.com",
            "password": "Password123!"
        }
    )

    assert response.status_code in (200, 201)


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    response = await client.post(
        "/auth/login",
        data={
            "username": "test@test.com",
            "password": "Password123!"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


# =====================================================
# USERS
# =====================================================

@pytest.mark.asyncio
async def test_get_users(admin_client: AsyncClient):
    response = await admin_client.get("/users/get_users/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_user(admin_client: AsyncClient):
    response = await admin_client.get("/users/get_user/1")

    assert response.status_code in (200, 404)


@pytest.mark.asyncio
async def test_delete_user(admin_client: AsyncClient):
    response = await admin_client.delete(
        "/users/delete_user/9999"
    )

    assert response.status_code in (200, 404)


# =====================================================
# EVENTS
# =====================================================

@pytest.mark.asyncio
async def test_create_event(org_client: AsyncClient):

    payload = {
        "title": "Tech Conference",
        "description": "Conference",
        "location": "Online",
        "capacity": 100
    }

    response = await org_client.post(
        "/events/create_event",
        json=payload
    )

    assert response.status_code in (200, 201)


@pytest.mark.asyncio
async def test_get_events(client: AsyncClient):
    response = await client.get("/events/get_events/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_event(client: AsyncClient):
    response = await client.get("/events/get_event/1")
    assert response.status_code in (200, 404)


@pytest.mark.asyncio
async def test_update_event(org_client: AsyncClient):
    response = await org_client.put(
        "/events/update_event/1",
        json={
            "title": "Updated Event"
        }
    )

    assert response.status_code in (
        200,
        404,
        422
    )


@pytest.mark.asyncio
async def test_delete_event(org_client: AsyncClient):
    response = await org_client.delete(
        "/events/delete_event/1"
    )

    assert response.status_code in (
        200,
        404
    )


# =====================================================
# REGISTRATIONS
# =====================================================

@pytest.mark.asyncio
async def test_register_event(
    client_user: AsyncClient
):
    response = await client_user.post(
        "/registrations/register/1"
    )

    assert response.status_code in (
        200,
        201,
        404,
        409
    )


@pytest.mark.asyncio
async def test_get_registration(
    client_user: AsyncClient
):
    response = await client_user.get(
        "/registrations/1"
    )

    assert response.status_code in (
        200,
        404
    )


@pytest.mark.asyncio
async def test_get_user_registrations(
    client_user: AsyncClient
):
    response = await client_user.get(
        "/registrations/user/1"
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_event_registrations(
    org_client: AsyncClient
):
    response = await org_client.get(
        "/registrations/event/1"
    )

    assert response.status_code in (
        200,
        404
    )


@pytest.mark.asyncio
async def test_cancel_registration(
    client_user: AsyncClient
):
    response = await client_user.delete(
        "/registrations/1"
    )

    assert response.status_code in (
        200,
        404
    )


# =====================================================
# ADMIN
# =====================================================

@pytest.mark.asyncio
async def test_admin_stats(
    admin_client: AsyncClient
):
    response = await admin_client.get(
        "/admin/stats"
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_promote_user(
    admin_client: AsyncClient
):
    response = await admin_client.post(
        "/admin/organizations/promote/1"
    )

    assert response.status_code in (
        200,
        404
    )


@pytest.mark.asyncio
async def test_demote_organization(
    admin_client: AsyncClient
):
    response = await admin_client.post(
        "/admin/organizations/demote/1"
    )

    assert response.status_code in (
        200,
        404
    )


@pytest.mark.asyncio
async def test_change_role(
    admin_client: AsyncClient
):
    response = await admin_client.put(
        "/admin/users/1/role",
        params={"role": "organization"}
    )

    assert response.status_code in (
        200,
        404
    )


@pytest.mark.asyncio
async def test_activate_user(
    admin_client: AsyncClient
):
    response = await admin_client.put(
        "/admin/users/1/activate"
    )

    assert response.status_code in (
        200,
        404
    )


@pytest.mark.asyncio
async def test_deactivate_user(
    admin_client: AsyncClient
):
    response = await admin_client.put(
        "/admin/users/1/deactivate"
    )

    assert response.status_code in (
        200,
        404
    )


@pytest.mark.asyncio
async def test_get_organizations(
    admin_client: AsyncClient
):
    response = await admin_client.get(
        "/admin/organizations"
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_organization_events(
    admin_client: AsyncClient
):
    response = await admin_client.get(
        "/admin/organizations/1/events"
    )

    assert response.status_code in (
        200,
        404
    )


@pytest.mark.asyncio
async def test_get_organization_registrations(
    admin_client: AsyncClient
):
    response = await admin_client.get(
        "/admin/organizations/1/registrations"
    )

    assert response.status_code in (
        200,
        404
    )


@pytest.mark.asyncio
async def test_admin_list_events(
    admin_client: AsyncClient
):
    response = await admin_client.get(
        "/admin/events"
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_admin_delete_event(
    admin_client: AsyncClient
):
    response = await admin_client.delete(
        "/admin/events/1"
    )

    assert response.status_code in (
        200,
        404
    )


@pytest.mark.asyncio
async def test_admin_list_registrations(
    admin_client: AsyncClient
):
    response = await admin_client.get(
        "/admin/registrations"
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_admin_get_registration(
    admin_client: AsyncClient
):
    response = await admin_client.get(
        "/admin/registrations/1"
    )

    assert response.status_code in (
        200,
        404
    )


@pytest.mark.asyncio
async def test_admin_delete_registration(
    admin_client: AsyncClient
):
    response = await admin_client.delete(
        "/admin/registrations/1"
    )

    assert response.status_code in (
        200,
        404
    )


@pytest.mark.asyncio
async def test_admin_update_registration_status(
    admin_client: AsyncClient
):
    response = await admin_client.put(
        "/admin/registrations/1/status",
        params={
            "status_val": "confirmed"
        }
    )

    assert response.status_code in (
        200,
        404
    )


# =====================================================
# AUTHORIZATION
# =====================================================

@pytest.mark.asyncio
async def test_user_cannot_access_admin(
    client_user: AsyncClient
):
    response = await client_user.get(
        "/admin/stats"
    )

    assert response.status_code in (
        401,
        403
    )


@pytest.mark.asyncio
async def test_anonymous_cannot_create_event(
    client: AsyncClient
):
    response = await client.post(
        "/events/create_event",
        json={}
    )

    assert response.status_code in (
        401,
        403
    )