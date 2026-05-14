from datetime import datetime

from pydantic import BaseModel


class PaymentRead(BaseModel):
    id: int
    telegram_id: int
    amount: int
    currency: str
    status: str
    provider: str
    created_at: datetime
    paid_at: datetime | None


class MockPaymentRead(BaseModel):
    payment: PaymentRead
    subscription_expires_at: datetime