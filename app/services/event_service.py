from app.models.event import Event
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.schemas.event import EventCreate
from fastapi import HTTPException, status
from app.services.user_service import UserOperations
from typing import Optional


class EventOperations:

    def __init__(self, db: Session = None):
        if db is None:
            self.db = next(get_db())
        else:
            self.db = db
        self.user_ops = UserOperations(db=self.db)

    def create_event(self, data: EventCreate, organizer_id: Optional[int] = None):
        existing_event = self.db.query(Event).filter(Event.title == data.title).first()
        if existing_event:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event with this title already exists"
            )

        db_event = Event(
            title=data.title,
            description=data.description,
            start_time=data.start_time,
            end_time=data.end_time,
            location=data.location,
            max_attendees=data.max_attendees,
            organizer_id=organizer_id,
        )
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return db_event

    def get_event_by_id(self, event_id: int):
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with id {event_id} not found"
            )
        return event

    def get_events(self, skip: int = 0, limit: int = 100):
        return self.db.query(Event).offset(skip).limit(limit).all()

    def update_event(self, event_id: int, **kwargs):
        db_event = self.get_event_by_id(event_id)
        for key, value in kwargs.items():
            if value is not None:
                setattr(db_event, key, value)
        self.db.commit()
        self.db.refresh(db_event)
        return db_event

    def delete_event(self, event_id: int):
        db_event = self.get_event_by_id(event_id)
        self.db.delete(db_event)
        self.db.commit()
        return db_event
