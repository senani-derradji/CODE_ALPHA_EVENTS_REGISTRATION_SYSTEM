from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.event import EventCreate, EventUpdate, EventResponse
from app.services.event_service import EventOperations
from app.depend.current_user import get_current_user, required_organization_or_admin
from app.services.user_service import UserOperations
from app.services.registration_service import RegistrationService


router = APIRouter()


@router.post("/create/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event: EventCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(required_organization_or_admin),
):
    event_ops = EventOperations(db)

    created_event = await event_ops.create_event(event, organizer_id=current_user.id)
    if not created_event:
        raise HTTPException(status_code=400, detail="Failed to create event")

    return created_event


@router.get("/get_events/", response_model=list[EventResponse])
async def get_events(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    event_ops = EventOperations(db)
    return await event_ops.get_events(skip, limit)


@router.get("/get_event/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db: AsyncSession = Depends(get_db)):
    event_ops = EventOperations(db)
    return await event_ops.get_event_by_id(event_id)


@router.put("/update_event/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event: EventUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(required_organization_or_admin),
):
    event_ops = EventOperations(db)
    return await event_ops.update_event(event_id, **event.model_dump(exclude_unset=True))


@router.get("/get_events_by_organizer/{organizer_id}", response_model=list[EventResponse])
async def get_events_by_organizer(
    organizer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(required_organization_or_admin)
):
    event_ops = EventOperations(db)
    return await event_ops.get_events_by_organizer(organizer_id)


@router.get("/count_events/", response_model=int)
async def count_events(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    event_ops = EventOperations(db)
    return await event_ops.count_events()


@router.get("check_user_in_event/{user_email}/{event_id}", response_model=bool)
async def check_user_in_event(
    event_id: int,
    user_email: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(required_organization_or_admin),
):
    event_ops = EventOperations(db)

    event = await event_ops.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    user_ops = UserOperations(db)

    user = await user_ops.get_user_by_email(user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    registration_ops = RegistrationService(db)

    registration = await registration_ops.is_user_registered(user.id, event_id)
    if not registration:
        raise HTTPException(status_code=404, detail="User not registered for this event")

    return registration


@router.get("/count_registrations")
async def count_registrations(db: AsyncSession = Depends(get_db)):
    registration_ops = RegistrationService(db)
    return await registration_ops.count_registrations()


@router.delete("/delete_event/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(required_organization_or_admin),
):
    event_ops = EventOperations(db)
    await event_ops.delete_event(event_id)
    return None
