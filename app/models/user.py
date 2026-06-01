from app.core.database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="user")
    updated_times = Column(Integer, default=0, nullable=True)
    is_active = Column(Integer, default=0)


    registrations = relationship("Registration", back_populates="user", cascade="all, delete-orphan")
    organized_events = relationship("Event", back_populates="organizer")
