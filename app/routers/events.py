from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.event import EventCreate, EventUpdate, EventResponse
from app.services.event_service import EventOperations
from app.depend.current_user import get_current_user, required_organization_or_admin
# from app.services.EMAIL_SERVICE.notification_service import NotificationService

router = APIRouter()


@router.post("/create/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user=Depends(required_organization_or_admin),
):
    event_ops = EventOperations(db)

    created_event = event_ops.create_event(event, organizer_id=current_user.id)
    if not created_event:
        raise HTTPException(status_code=400, detail="Failed to create event")

    return created_event


@router.get("/get_events/", response_model=list[EventResponse])
async def get_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    event_ops = EventOperations(db)
    return event_ops.get_events(skip, limit)


@router.get("/get_event/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    event_ops = EventOperations(db)
    return event_ops.get_event_by_id(event_id)


@router.put("/update_event/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event: EventUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(required_organization_or_admin),
):
    event_ops = EventOperations(db)
    return event_ops.update_event(event_id, **event.model_dump(exclude_unset=True))


@router.delete("/delete_event/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(required_organization_or_admin),
):
    event_ops = EventOperations(db)
    event_ops.delete_event(event_id)
    return None
