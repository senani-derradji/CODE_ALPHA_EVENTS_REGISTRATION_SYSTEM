from app.core.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.schema import UniqueConstraint


class Registration(Base):
    __tablename__ = "registrations"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "event_id",
            name="unique_user_event"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, index=True, default="pending")


    event = relationship("Event", back_populates="registrations")
    user = relationship("User", back_populates="registrations")

    registered_at = Column(DateTime(timezone=True), server_default=func.now() )
