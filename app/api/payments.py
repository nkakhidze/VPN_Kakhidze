from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.payment import MockPaymentRead
from app.services.payment_service import create_mock_payment


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@router.post("/mock/{telegram_id}", response_model=MockPaymentRead)
def mock_payment(
    telegram_id: int,
    db: Session = Depends(get_db),
):
    return create_mock_payment(db=db, telegram_id=telegram_id)