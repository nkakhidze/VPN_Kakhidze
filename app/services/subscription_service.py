from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import User


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

    if user.subscription_expires_at is None:
        user.subscription_expires_at = now + timedelta(days=SUBSCRIPTION_DAYS)
    elif user.subscription_expires_at <= now:
        user.subscription_expires_at = now + timedelta(days=SUBSCRIPTION_DAYS)
    else:
        user.subscription_expires_at += timedelta(days=SUBSCRIPTION_DAYS)

    db.commit()
    db.refresh(user)

    return user

