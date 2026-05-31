from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
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


@router.get("/stats")
async def admin_stats(db: Session = Depends(get_db), admin=Depends(required_admin)):
    total_users = db.query(User).count()
    total_events = db.query(Event).count()
    total_registrations = db.query(Registration).count()
    users_by_role = db.query(User.role, func.count(User.id)).group_by(User.role).all()
    registrations_by_status = db.query(Registration.status, func.count(Registration.id)).group_by(Registration.status).all()
    top_events = (
        db.query(Event.id, Event.title, func.count(Registration.id).label("reg_count"))
        .outerjoin(Registration, Registration.event_id == Event.id)
        .group_by(Event.id)
        .order_by(func.count(Registration.id).desc())
        .limit(5)
        .all()
    )
    return {
        "totals": {
            "users": total_users,
            "events": total_events,
            "registrations": total_registrations,
        },
        "users_by_role": {role: count for role, count in users_by_role},
        "registrations_by_status": {status_val: count for status_val, count in registrations_by_status},
        "top_events": [{"id": e.id, "title": e.title, "registrations": e.reg_count} for e in top_events],
    }


@router.get("/users", response_model=list[UserResponse])
async def admin_list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin=Depends(required_admin),
):
    return db.query(User).offset(skip).limit(limit).all()


@router.get("/users/{user_id}", response_model=UserResponse)
async def admin_get_user(user_id: int, db: Session = Depends(get_db), admin=Depends(required_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/users/{user_id}/role")
async def admin_change_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    admin=Depends(required_admin),
):
    if role not in ("user", "organization", "admin"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role. Must be 'user', 'organization', or 'admin'")
    user_ops = UserOperations(db)
    user = user_ops.update_user(user_id, role=role)
    return {"id": user.id, "username": user.username, "role": user.role}


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_user(user_id: int, db: Session = Depends(get_db), admin=Depends(required_admin)):
    user_ops = UserOperations(db)
    user_ops.delete_user(user_id)
    return None


@router.get("/events", response_model=list[EventResponse])
async def admin_list_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin=Depends(required_admin),
):
    return db.query(Event).offset(skip).limit(limit).all()


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_event(event_id: int, db: Session = Depends(get_db), admin=Depends(required_admin)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    db.delete(event)
    db.commit()
    return None


@router.get("/registrations", response_model=list[RegstrationResponse])
async def admin_list_registrations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin=Depends(required_admin),
):
    return db.query(Registration).offset(skip).limit(limit).all()


@router.put("/registrations/{registration_id}/status")
async def admin_update_registration_status(
    registration_id: int,
    status_val: str,
    db: Session = Depends(get_db),
    admin=Depends(required_admin),
):
    if status_val not in ("pending", "confirmed", "cancelled"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
    reg = db.query(Registration).filter(Registration.id == registration_id).first()
    if not reg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")
    reg.status = status_val
    db.commit()
    db.refresh(reg)
    return reg


@router.get("/organizers", response_model=list[UserResponse])
async def admin_list_organizers(db: Session = Depends(get_db), admin=Depends(required_admin)):
    return db.query(User).filter(User.role == "organization").all()


@router.post("/organizers/promote/{user_id}", response_model=UserResponse)
async def admin_promote_to_organizer(user_id: int, db: Session = Depends(get_db), admin=Depends(required_admin)):
    user_ops = UserOperations(db)
    return user_ops.update_user(user_id, role="organization")


@router.post("/organizers/demote/{user_id}", response_model=UserResponse)
async def admin_demote_organizer(user_id: int, db: Session = Depends(get_db), admin=Depends(required_admin)):
    user_ops = UserOperations(db)
    return user_ops.update_user(user_id, role="user")
