from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SubscriptionReminderRead(BaseModel):
    telegram_id: int
    remind_at: datetime
    days_left: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubscriptionReminderWithUserRead(BaseModel):
    telegram_id: int
    first_name: str | None = None
    username: str | None = None
    remind_at: datetime
    days_left: int
    created_at: datetime


class RebuildSubscriptionRemindersResult(BaseModel):
    deleted_count: int
    created_count: int