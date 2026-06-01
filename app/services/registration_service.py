from app.models.registration import Registration
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user_service import UserOperations
from app.services.event_service import EventOperations
from app.schemas.registration import RegistrationCreate
from fastapi import HTTPException, status
from sqlalchemy import select


class RegistrationService:

    def __init__(self, db: AsyncSession = None):
        if db is None:
            self.db = next(get_db())
        else:
            self.db = db

        self.userops = UserOperations(db=self.db)
        self.eventops = EventOperations(db=self.db)

    async def create_registration(self, data: RegistrationCreate):
        user_id = data.user_id
        event_id = data.event_id

        user = await self.userops.get_user_by_id(user_id)
        if not user:
            raise HTTPException(404, f"User with id {user_id} not found")

        event = await self.eventops.get_event_by_id(event_id)
        if not event:
            raise HTTPException(404, f"Event with id {event_id} not found")

        existing = await self.db.execute(
            select(Registration).where(
                Registration.user_id == user_id,
                Registration.event_id == event_id
            )
        )
        if existing.scalars().first():
            raise HTTPException(400, "User already registered for this event")

        current = await self.db.execute(
            select(Registration).where(Registration.event_id == event_id)
        )

        if len(current.scalars().all()) >= event.max_attendees:
            raise HTTPException(400, "Event is at maximum capacity")

        db_registration = Registration(
            user_id=user_id,
            event_id=event_id,
            status="Completed"
        )

        self.db.add(db_registration)
        await self.db.commit()
        await self.db.refresh(db_registration)

        return db_registration

    async def get_registrations_by_user(self, user_id: int):
        result = await self.db.execute(
            select(Registration).where(Registration.user_id == user_id)
        )
        return result.scalars().all()

    async def get_registrations_by_event(self, event_id: int):
        result = await self.db.execute(
            select(Registration).where(Registration.event_id == event_id)
        )
        return result.scalars().all()

    async def get_registration_by_id(self, registration_id: int):
        result = await self.db.execute(
            select(Registration).where(Registration.id == registration_id)
        )
        reg = result.scalars().first()

        if not reg:
            raise HTTPException(404, f"Registration with id {registration_id} not found")

        return reg

    async def cancel_registration(self, registration_id: int):
        reg = await self.get_registration_by_id(registration_id)

        await self.db.delete(reg)
        await self.db.commit()

        return reg

    async def is_user_registered(self, user_id: int, event_id: int) -> bool:
        result = await self.db.execute(
            select(Registration).where(
                Registration.user_id == user_id,
                Registration.event_id == event_id
            )
        )
        return result.scalars().first() is not None

    async def count_registrations(self) -> int:
        result = await self.db.execute(
            select(Registration)
        )
        return len(result.scalars().all())