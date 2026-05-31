from app.models.registration import Registration
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.services.user_service import UserOperations
from app.services.event_service import EventOperations
from app.schemas.registration import RegistrationCreate
from fastapi import HTTPException, status

class RegistrationService:

    def __init__(self, db: Session = None):
        if db is None:
            self.db = next(get_db())
        else:
            self.db = db
        self.userops = UserOperations(db=self.db)
        self.eventops = EventOperations(db=self.db)

    def create_registration(self, data: RegistrationCreate):
        user_id = data.user_id
        event_id = data.event_id

        try:
            user = self.userops.get_user_by_id(user_id)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )

        try:
            event = self.eventops.get_event_by_id(event_id)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with id {event_id} not found"
            )

        existing = self.db.query(Registration).filter(
            Registration.user_id == user_id,
            Registration.event_id == event_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already registered for this event"
            )

        current_registrations = self.db.query(Registration).filter(
            Registration.event_id == event_id
        ).count()

        if current_registrations >= event.max_attendees:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event is at maximum capacity"
            )

        db_registration = Registration(user_id=user_id, event_id=event_id)

        self.db.add(db_registration)
        self.db.commit()
        self.db.refresh(db_registration)
        return db_registration

    def get_registrations_by_user(self, user_id: int):
        try:
            self.userops.get_user_by_id(user_id)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )

        registrations = self.db.query(Registration).filter(Registration.user_id == user_id).all()
        return registrations

    def get_registrations_by_event(self, event_id: int):

        try:
            self.eventops.get_event_by_id(event_id)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with id {event_id} not found"
            )

        registrations = self.db.query(Registration).filter(Registration.event_id == event_id).all()
        return registrations

    def get_registration_by_id(self, registration_id: int):
        registration = self.db.query(Registration).filter(Registration.id == registration_id).first()
        if not registration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registration with id {registration_id} not found"
            )
        return registration

    def cancel_registration(self, registration_id: int):
        db_registration = self.get_registration_by_id(registration_id)
        if db_registration:
            self.db.delete(db_registration)
            self.db.commit()
            return db_registration
        return None