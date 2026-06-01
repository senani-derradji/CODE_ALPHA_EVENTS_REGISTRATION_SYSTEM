from app.models.event import Event
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.event import EventCreate
from fastapi import HTTPException, status
from app.services.user_service import UserOperations
from typing import Optional
from sqlalchemy import select, func


class EventOperations:

    def __init__(self, db: AsyncSession = None):
        if db is None:
            self.db = next(get_db())  # ⚠️ better inject from router (keep your style)
        else:
            self.db = db

        self.user_ops = UserOperations(db=self.db)

    async def create_event(self, data: EventCreate, organizer_id: Optional[int] = None):

        result = await self.db.execute(
            select(Event).where(Event.title == data.title)
        )
        existing_event = result.scalars().first()

        if not organizer_id:
            pass

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
        await self.db.commit()
        await self.db.refresh(db_event)

        return db_event

    async def get_event_by_id(self, event_id: int):
        result = await self.db.execute(
            select(Event).where(Event.id == event_id)
        )
        event = result.scalars().first()

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with id {event_id} not found"
            )
        return event

    async def get_events(self, skip: int = 0, limit: int = 100):
        result = await self.db.execute(
            select(Event).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update_event(self, event_id: int, **kwargs):
        db_event = await self.get_event_by_id(event_id)

        for key, value in kwargs.items():
            if value is not None:
                setattr(db_event, key, value)

        await self.db.commit()
        await self.db.refresh(db_event)
        return db_event

    async def delete_event(self, event_id: int):
        db_event = await self.get_event_by_id(event_id)

        await self.db.delete(db_event)
        await self.db.commit()

        return db_event

    async def get_events_by_organizer(self, organizer_id: int):
        result = await self.db.execute(
            select(Event).where(Event.organizer_id == organizer_id)
        )
        events = result.scalars().all()

        if not events:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No events found for organizer with id {organizer_id}"
            )
        return events

    async def count_events(self) -> int:
        result = await self.db.execute(
            select(func.count(Event.id))
        )
        return result.scalar()