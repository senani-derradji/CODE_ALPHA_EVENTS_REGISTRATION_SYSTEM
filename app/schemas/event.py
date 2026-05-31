from pydantic import BaseModel, field_validator, model_validator
from datetime import datetime
from typing import Optional


class EventBase(BaseModel):
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    location: str
    max_attendees: int

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3 or len(v) > 200:
            raise ValueError("Title must be between 3 and 200 characters")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 10 or len(v) > 5000:
            raise ValueError("Description must be between 10 and 5000 characters")
        return v

    @field_validator("location")
    @classmethod
    def validate_location(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 300:
            raise ValueError("Location must be between 2 and 300 characters")
        return v

    @field_validator("max_attendees")
    @classmethod
    def validate_max_attendees(cls, v: int) -> int:
        if v < 1 or v > 100000:
            raise ValueError("max_attendees must be between 1 and 100000")
        return v

    @model_validator(mode="after")
    def validate_times(self) -> "EventBase":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self

    class Config:
        from_attributes = True


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    max_attendees: Optional[int] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) < 3 or len(v) > 200:
            raise ValueError("Title must be between 3 and 200 characters")
        return v

    @field_validator("max_attendees")
    @classmethod
    def validate_max_attendees(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        if v < 1 or v > 100000:
            raise ValueError("max_attendees must be between 1 and 100000")
        return v

    class Config:
        from_attributes = True


class EventResponse(EventBase):
    id: int
    organizer_id: Optional[int] = None

    class Config:
        from_attributes = True
