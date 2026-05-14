from datetime import datetime, time

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import SubscriptionReminder, User
from app.services.subscription_service import (
    get_subscription_status,
    should_remind_about_subscription,
)


def build_today_remind_at() -> datetime:
    today = datetime.now().date()

    return datetime.combine(
        today,
        time(hour=10, minute=0),
    )


def rebuild_subscription_reminders(session: Session) -> tuple[int, int]:
    """
    Полностью пересобирает актуальную очередь напоминаний.

    Логика:
    1. Удаляем все записи из subscription_reminders.
    2. Проходим по пользователям.
    3. Если подписка активна и осталось 1–3 дня —
       создаём одну запись в subscription_reminders.
    """

    deleted_count = session.query(SubscriptionReminder).delete()

    users = session.scalars(select(User)).all()

    created_count = 0
    remind_at = build_today_remind_at()

    for user in users:
        if not should_remind_about_subscription(session, user.telegram_id):
            continue

        subscription_status = get_subscription_status(session, user.telegram_id)

        reminder = SubscriptionReminder(
            telegram_id=user.telegram_id,
            remind_at=remind_at,
            days_left=subscription_status.days_left,
        )

        session.add(reminder)
        created_count += 1

    session.commit()

    return deleted_count, created_count


def get_due_subscription_reminders(session: Session) -> list[tuple[SubscriptionReminder, User]]:
    """
    Возвращает напоминания, у которых уже наступило remind_at.
    Сразу возвращает и User, чтобы бот получил first_name/username.
    """

    now = datetime.now()

    statement = (
        select(SubscriptionReminder, User)
        .join(User, User.telegram_id == SubscriptionReminder.telegram_id)
        .where(SubscriptionReminder.remind_at <= now)
    )

    return list(session.execute(statement).all())


def delete_subscription_reminder(
    session: Session,
    telegram_id: int,
) -> None:
    statement = delete(SubscriptionReminder).where(
        SubscriptionReminder.telegram_id == telegram_id
    )

    session.execute(statement)
    session.commit()