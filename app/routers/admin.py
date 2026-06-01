from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.depend.current_user import required_admin

from app.models.user import User
from app.models.event import Event
from app.models.registration import Registration

from app.schemas.user import UserResponse
from app.schemas.event import EventResponse
from app.schemas.registration import RegstrationResponse

from app.services.user_service import UserOperations
from app.services.event_service import EventOperations
from app.services.registration_service import RegistrationService


router = APIRouter()


@router.get("/stats")
async def admin_stats(
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin)
):
    total_users = (
        await db.execute(select(func.count(User.id)))
    ).scalar()

    total_events = (
        await db.execute(select(func.count(Event.id)))
    ).scalar()

    total_registrations = (
        await db.execute(select(func.count(Registration.id)))
    ).scalar()

    users_by_role = (
        await db.execute(
            select(
                User.role,
                func.count(User.id)
            ).group_by(User.role)
        )
    ).all()

    registrations_by_status = (
        await db.execute(
            select(
                Registration.status,
                func.count(Registration.id)
            ).group_by(Registration.status)
        )
    ).all()

    active_users = (
        await db.execute(
            select(func.count(User.id))
            .where(User.is_active == 1)
        )
    ).scalar()

    inactive_users = (
        await db.execute(
            select(func.count(User.id))
            .where(User.is_active == 0)
        )
    ).scalar()

    organizations = (
        await db.execute(
            select(func.count(User.id))
            .where(User.role == "organization")
        )
    ).scalar()

    admins = (
        await db.execute(
            select(func.count(User.id))
            .where(User.role == "admin")
        )
    ).scalar()

    top_events = (
        await db.execute(
            select(
                Event.id,
                Event.title,
                func.count(Registration.id).label("registrations")
            )
            .outerjoin(
                Registration,
                Registration.event_id == Event.id
            )
            .group_by(Event.id)
            .order_by(
                func.count(Registration.id).desc()
            )
            .limit(10)
        )
    ).all()

    return {
        "totals": {
            "users": total_users,
            "events": total_events,
            "registrations": total_registrations
        },
        "active_users": active_users,
        "inactive_users": inactive_users,
        "organizations": organizations,
        "admins": admins,
        "users_by_role": {
            role: count
            for role, count in users_by_role
        },
        "registrations_by_status": {
            status: count
            for status, count in registrations_by_status
        },
        "top_events": [
            {
                "id": e.id,
                "title": e.title,
                "registrations": e.registrations
            }
            for e in top_events
        ]
    }



@router.put("/users/{user_id}/role")
async def change_user_role(
    user_id: int,
    role: str,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin)
):
    if role not in (
        "user",
        "organization",
        "admin"
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    user_ops = UserOperations(db)

    return await user_ops.update_user(
        user_id,
        role=role
    )


@router.post("/organizations/promote/{user_id}")
async def promote_to_organization(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin)
):
    user_ops = UserOperations(db)

    return await user_ops.update_user(
        user_id,
        role="organization"
    )


@router.post("/organizations/demote/{user_id}")
async def demote_organization(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin)
):
    user_ops = UserOperations(db)

    return await user_ops.update_user(
        user_id,
        role="user"
    )



@router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin)
):
    user_ops = UserOperations(db)

    return await user_ops.update_user(
        user_id,
        is_active=1
    )


@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin)
):
    user_ops = UserOperations(db)

    return await user_ops.update_user(
        user_id,
        is_active=0
    )



@router.get(
    "/organizations",
    response_model=list[UserResponse]
)
async def get_organizations(
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin)
):
    result = await db.execute(
        select(User)
        .where(User.role == "organization")
    )

    return result.scalars().all()


@router.get(
    "/organizations/{organization_id}/events",
    response_model=list[EventResponse]
)
async def get_organization_events(
    organization_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin)
):
    event_ops = EventOperations(db)

    return await event_ops.get_events_by_organizer(
        organization_id
    )


@router.get(
    "/organizations/{organization_id}/registrations",
    response_model=list[RegstrationResponse]
)
async def get_organization_registrations(
    organization_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin)
):
    events = (
        await db.execute(
            select(Event.id)
            .where(
                Event.organizer_id ==
                organization_id
            )
        )
    ).scalars().all()

    if not events:
        return []

    result = await db.execute(
        select(Registration)
        .where(
            Registration.event_id.in_(events)
        )
    )

    return result.scalars().all()



@router.get(
    "/events",
    response_model=list[EventResponse]
)
async def list_events(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin)
):
    result = await db.execute(
        select(Event)
        .offset(skip)
        .limit(limit)
    )

    return result.scalars().all()


@router.delete("/events/{event_id}")
async def delete_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin)
):
    event_ops = EventOperations(db)

    return await event_ops.delete_event(
        event_id
    )


@router.get(
    "/registrations",
    response_model=list[RegstrationResponse]
)
async def list_registrations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin)
):
    result = await db.execute(
        select(Registration)
        .offset(skip)
        .limit(limit)
    )

    return result.scalars().all()


@router.get(
    "/registrations/{registration_id}",
    response_model=RegstrationResponse
)
async def get_registration(
    registration_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin)
):
    reg_service = RegistrationService(db)

    return await reg_service.get_registration_by_id(
        registration_id
    )


@router.delete(
    "/registrations/{registration_id}"
)
async def delete_registration(
    registration_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin)
):
    reg_service = RegistrationService(db)

    return await reg_service.cancel_registration(
        registration_id
    )


@router.put(
    "/registrations/{registration_id}/status"
)
async def update_registration_status(
    registration_id: int,
    status_val: str,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin)
):
    if status_val not in (
        "pending",
        "confirmed",
        "cancelled"
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )

    result = await db.execute(
        select(Registration)
        .where(
            Registration.id ==
            registration_id
        )
    )

    registration = result.scalars().first()

    if not registration:
        raise HTTPException(
            status_code=404,
            detail="Registration not found"
        )

    registration.status = status_val

    await db.commit()
    await db.refresh(registration)

    return registration