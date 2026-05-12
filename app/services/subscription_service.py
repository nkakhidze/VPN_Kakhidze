from datetime import datetime, timedelta

from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.database import get_db
from app.schemas.user import SubscriptionStatusRead, UserRead


SUBSCRIPTION_DAYS = 30

def extend_subscription(db: Session, telegram_id: int) -> User:
    user = db.query(User).filter(
        User.telegram_id == telegram_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    now = datetime.now()

    if user.subscription_expires_at is None or (user.subscription_expires_at <= now):
        user.subscription_expires_at = now + timedelta(days=SUBSCRIPTION_DAYS)
    else:
        user.subscription_expires_at += timedelta(days=SUBSCRIPTION_DAYS)

    db.commit()
    db.refresh(user)

    return user


def get_subscription_status(db: Session, telegram_id: int) -> SubscriptionStatusRead:
    user = db.query(User).filter(
        User.telegram_id == telegram_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    now = datetime.now()

    if user.subscription_expires_at is None or user.subscription_expires_at <= now:
        return SubscriptionStatusRead(
            telegram_id=user.telegram_id,
            is_active=False,
            subscription_expires_at=user.subscription_expires_at,
            days_left=0
        )
    else:
        return SubscriptionStatusRead(
            telegram_id=user.telegram_id,
            is_active=True,
            subscription_expires_at=user.subscription_expires_at,
            days_left=(user.subscription_expires_at - now).days,
        )
