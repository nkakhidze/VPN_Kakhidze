from datetime import datetime
from pydantic import BaseModel
from pydantic import ConfigDict


class UserCreate(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None


class UserUpdate(BaseModel):
    username: str | None = None
    first_name: str | None = None
    subscription_expires_at: datetime | None = None
    last_reminded_at: datetime | None = None


class UserRead(BaseModel):
    telegram_id: int
    username: str | None
    first_name: str | None
    subscription_expires_at: datetime | None
    last_reminded_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)