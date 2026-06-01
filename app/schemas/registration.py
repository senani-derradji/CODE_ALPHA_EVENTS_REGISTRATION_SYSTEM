from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Literal

VALID_STATUSES = {"pending", "confirmed", "cancelled"}

class RegistrationCreate(BaseModel):
    user_id: int
    event_id: int
    status: str | None = None

    @field_validator("user_id", "event_id")
    @classmethod
    def validate_positive_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("ID must be a positive integer")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in VALID_STATUSES:
            raise ValueError(f"status must be one of {VALID_STATUSES}")
        return v

    class Config:
        from_attributes = True


class RegstrationResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    status: str
    registered_at: datetime | None = None

    class Config:
        from_attributes = True
