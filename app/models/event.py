from app.core.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime, index=True)
    location = Column(String, index=True)
    max_attendees = Column(Integer, index=True)
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    organizer = relationship("User", back_populates="organized_events")
    registrations = relationship("Registration", back_populates="event", cascade="all, delete-orphan")
