from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.subscription_reminder import (
    RebuildSubscriptionRemindersResult,
    SubscriptionReminderWithUserRead,
)
from app.services.subscription_reminder_service import (
    delete_subscription_reminder,
    get_due_subscription_reminders,
    rebuild_subscription_reminders,
)


router = APIRouter(
    prefix="/subscription-reminders",
    tags=["Subscription reminders"],
)


@router.post(
    "/rebuild",
    response_model=RebuildSubscriptionRemindersResult,
)
def rebuild_reminders(
    db: Session = Depends(get_db),
):
    deleted_count, created_count = rebuild_subscription_reminders(db)

    return RebuildSubscriptionRemindersResult(
        deleted_count=deleted_count,
        created_count=created_count,
    )


@router.get(
    "/due",
    response_model=list[SubscriptionReminderWithUserRead],
)
def get_due_reminders(
    db: Session = Depends(get_db),
):
    reminders_with_users = get_due_subscription_reminders(db)

    result = []

    for reminder, user in reminders_with_users:
        result.append(
            SubscriptionReminderWithUserRead(
                telegram_id=user.telegram_id,
                first_name=user.first_name,
                username=user.username,
                remind_at=reminder.remind_at,
                days_left=reminder.days_left,
                created_at=reminder.created_at,
            )
        )

    return result


@router.delete(
    "/{telegram_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_reminder(
    telegram_id: int,
    db: Session = Depends(get_db),
):
    delete_subscription_reminder(db, telegram_id)