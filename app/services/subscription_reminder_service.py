from datetime import UTC, datetime, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import SubscriptionReminder, User
from app.services.subscription_service import (
    get_subscription_status,
    should_remind_about_subscription,
)

DEFAULT_TIMEZONE = "Europe/Moscow"


def get_valid_timezone(timezone_name: str | None) -> ZoneInfo:
    if not timezone_name:
        return ZoneInfo(DEFAULT_TIMEZONE)

    return ZoneInfo(timezone_name)



def build_user_today_remind_at_utc(user_timezone: str | None) -> datetime:
    """
    Возвращает момент, когда у пользователя сегодня будет 10:00,
    но в UTC и без timezone-info.

    Пример:
    10:00 Asia/Tomsk -> 03:00 UTC
    10:00 Europe/Moscow -> 07:00 UTC
    """

    timezone = get_valid_timezone(user_timezone)

    now_for_user = datetime.now(timezone)
    user_today = now_for_user.date()

    user_10_am = datetime.combine(
        user_today,
        time(hour=10, minute=0),
        tzinfo=timezone,
    )

    remind_at_utc = user_10_am.astimezone(UTC)

    return remind_at_utc.replace(tzinfo=None)


def rebuild_subscription_reminders(session: Session) -> tuple[int, int]:
    """
    Полностью пересобирает актуальную очередь напоминаний.

    Логика:
    1. Удаляем все записи из subscription_reminders.
    2. Проходим по пользователям.
    3. Если подписка активна и осталось 1–3 дня —
       создаём одну запись.
    4. remind_at считаем как сегодняшние 10:00
       в часовом поясе конкретного пользователя.
    """

    deleted_count = session.query(SubscriptionReminder).delete()

    users = session.scalars(select(User)).all()

    created_count = 0

    for user in users:
        if not should_remind_about_subscription(session, user.telegram_id):
            continue

        subscription_status = get_subscription_status(session, user.telegram_id)

        reminder = SubscriptionReminder(
            telegram_id=user.telegram_id,
            remind_at=build_user_today_remind_at_utc(user.timezone),
            days_left=subscription_status.days_left,
        )

        session.add(reminder)
        created_count += 1

    session.commit()

    return deleted_count, created_count


def get_due_subscription_reminders(session: Session) -> list[tuple[SubscriptionReminder, User]]:
    """
    Возвращает напоминания, у которых уже наступило remind_at.
    remind_at хранится в UTC без tzinfo.
    Поэтому сравниваем с datetime.utcnow().
    """

    now_utc = datetime.utcnow()

    statement = (
        select(SubscriptionReminder, User)
        .join(User, User.telegram_id == SubscriptionReminder.telegram_id)
        .where(SubscriptionReminder.remind_at <= now_utc)
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