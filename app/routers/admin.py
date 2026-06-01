from fastapi import APIRouter, Depends, HTTPException, status
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

router = APIRouter()


# =========================
# STATS
# =========================
@router.get("/stats")
async def admin_stats(
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin)
):

    total_users = (await db.execute(select(func.count(User.id)))).scalar()
    total_events = (await db.execute(select(func.count(Event.id)))).scalar()
    total_registrations = (await db.execute(select(func.count(Registration.id)))).scalar()

    users_by_role = (await db.execute(
        select(User.role, func.count(User.id)).group_by(User.role)
    )).all()

    registrations_by_status = (await db.execute(
        select(Registration.status, func.count(Registration.id))
        .group_by(Registration.status)
    )).all()

    top_events = (await db.execute(
        select(
            Event.id,
            Event.title,
            func.count(Registration.id).label("reg_count")
        )
        .outerjoin(Registration, Registration.event_id == Event.id)
        .group_by(Event.id)
        .order_by(func.count(Registration.id).desc())
        .limit(5)
    )).all()

    return {
        "totals": {
            "users": total_users,
            "events": total_events,
            "registrations": total_registrations,
        },
        "users_by_role": {r: c for r, c in users_by_role},
        "registrations_by_status": {s: c for s, c in registrations_by_status},
        "top_events": [
            {"id": e.id, "title": e.title, "registrations": e.reg_count}
            for e in top_events
        ],
    }


# =========================
# USERS
# =========================
@router.get("/users", response_model=list[UserResponse])
async def admin_list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin),
):
    result = await db.execute(
        select(User).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.get("/users/{user_id}", response_model=UserResponse)
async def admin_get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin)
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(404, "User not found")

    return user


@router.put("/users/{user_id}/role")
async def admin_change_role(
    user_id: int,
    role: str,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin),
):
    if role not in ("user", "organization", "admin"):
        raise HTTPException(400, "Invalid role")

    user_ops = UserOperations(db)
    return await user_ops.update_user(user_id, role=role)


@router.delete("/users/{user_id}")
async def admin_delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin)
):
    user_ops = UserOperations(db)
    await user_ops.delete_user(user_id)
    return None


# =========================
# EVENTS
# =========================
@router.get("/events", response_model=list[EventResponse])
async def admin_list_events(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin),
):
    result = await db.execute(
        select(Event).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.delete("/events/{event_id}")
async def admin_delete_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin)
):
    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = result.scalars().first()

    if not event:
        raise HTTPException(404, "Event not found")

    await db.delete(event)
    await db.commit()
    return None


# =========================
# REGISTRATIONS
# =========================
@router.get("/registrations", response_model=list[RegstrationResponse])
async def admin_list_registrations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin),
):
    result = await db.execute(
        select(Registration).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.put("/registrations/{registration_id}/status")
async def admin_update_registration_status(
    registration_id: int,
    status_val: str,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin),
):

    if status_val not in ("pending", "confirmed", "cancelled"):
        raise HTTPException(400, "Invalid status")

    result = await db.execute(
        select(Registration).where(Registration.id == registration_id)
    )
    reg = result.scalars().first()

    if not reg:
        raise HTTPException(404, "Registration not found")

    reg.status = status_val
    await db.commit()
    await db.refresh(reg)

    return reg


@router.get("/organizers", response_model=list[UserResponse])
async def admin_list_organizers(
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin),
):
    result = await db.execute(
        select(User).where(User.role == "organization")
    )
    return result.scalars().all()


@router.post("/organizers/promote/{user_id}", response_model=UserResponse)
async def admin_promote_to_organizer(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin)
):
    user_ops = UserOperations(db)
    return await user_ops.update_user(user_id, role="organization")


@router.post("/organizers/demote/{user_id}", response_model=UserResponse)
async def admin_demote_organizer(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(required_admin)
):
    user_ops = UserOperations(db)
    return await user_ops.update_user(user_id, role="user")