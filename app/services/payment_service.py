from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import Payment, User
from app.services.subscription_service import extend_subscription


MOCK_PAYMENT_AMOUNT = 300


def create_mock_payment(db: Session, telegram_id: int) -> dict:
    user = db.query(User).filter(
        User.telegram_id == telegram_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    payment = Payment(
        telegram_id=telegram_id,
        amount=MOCK_PAYMENT_AMOUNT,
        currency="RUB",
        status="succeeded",
        provider="mock",
        paid_at=datetime.utcnow(),
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    updated_user = extend_subscription(db=db, telegram_id=telegram_id)

    return {
        "payment": payment,
        "subscription_expires_at": updated_user.subscription_expires_at,
    }