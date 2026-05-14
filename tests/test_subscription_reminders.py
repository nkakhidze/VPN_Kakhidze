from datetime import datetime, timedelta

from app.db.models import SubscriptionReminder, User
from tests.conftest import TestingSessionLocal


def create_user(
    telegram_id: int,
    subscription_expires_at: datetime | None,
    username: str | None = None,
    first_name: str | None = None,
):
    db = TestingSessionLocal()

    try:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            subscription_expires_at=subscription_expires_at,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    finally:
        db.close()


def create_subscription_reminder(
    telegram_id: int,
    remind_at: datetime,
    days_left: int,
):
    db = TestingSessionLocal()

    try:
        reminder = SubscriptionReminder(
            telegram_id=telegram_id,
            remind_at=remind_at,
            days_left=days_left,
        )

        db.add(reminder)
        db.commit()
        db.refresh(reminder)

        return reminder

    finally:
        db.close()


def test_rebuild_subscription_reminders_creates_reminder_for_user_with_3_days_left(client):
    telegram_id = 1001

    create_user(
        telegram_id=telegram_id,
        username="test_user",
        first_name="Nick",
        subscription_expires_at=datetime.now() + timedelta(days=3),
    )

    response = client.post("/subscription-reminders/rebuild")

    assert response.status_code == 200

    body = response.json()

    assert body["deleted_count"] == 0
    assert body["created_count"] == 1

    db = TestingSessionLocal()

    try:
        reminder = db.query(SubscriptionReminder).filter(
            SubscriptionReminder.telegram_id == telegram_id
        ).first()

        assert reminder is not None
        assert reminder.telegram_id == telegram_id
        assert reminder.days_left == 2 or reminder.days_left == 3

    finally:
        db.close()


def test_rebuild_subscription_reminders_does_not_create_reminder_for_user_with_many_days_left(client):
    telegram_id = 1002

    create_user(
        telegram_id=telegram_id,
        username="test_user",
        first_name="Nick",
        subscription_expires_at=datetime.now() + timedelta(days=10),
    )

    response = client.post("/subscription-reminders/rebuild")

    assert response.status_code == 200

    body = response.json()

    assert body["deleted_count"] == 0
    assert body["created_count"] == 0

    db = TestingSessionLocal()

    try:
        reminder = db.query(SubscriptionReminder).filter(
            SubscriptionReminder.telegram_id == telegram_id
        ).first()

        assert reminder is None

    finally:
        db.close()


def test_get_due_subscription_reminders_returns_reminder_with_user_data(client):
    telegram_id = 1003

    create_user(
        telegram_id=telegram_id,
        username="test_user",
        first_name="Nick",
        subscription_expires_at=datetime.now() + timedelta(days=2),
    )

    create_subscription_reminder(
        telegram_id=telegram_id,
        remind_at=datetime.now() - timedelta(minutes=1),
        days_left=2,
    )

    response = client.get("/subscription-reminders/due")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["telegram_id"] == telegram_id
    assert body[0]["first_name"] == "Nick"
    assert body[0]["username"] == "test_user"
    assert body[0]["days_left"] == 2


def test_get_due_subscription_reminders_does_not_return_future_reminder(client):
    telegram_id = 1004

    create_user(
        telegram_id=telegram_id,
        username="test_user",
        first_name="Nick",
        subscription_expires_at=datetime.now() + timedelta(days=2),
    )

    create_subscription_reminder(
        telegram_id=telegram_id,
        remind_at=datetime.now() + timedelta(hours=1),
        days_left=2,
    )

    response = client.get("/subscription-reminders/due")

    assert response.status_code == 200

    body = response.json()

    assert body == []


def test_delete_subscription_reminder(client):
    telegram_id = 1005

    create_user(
        telegram_id=telegram_id,
        username="test_user",
        first_name="Nick",
        subscription_expires_at=datetime.now() + timedelta(days=2),
    )

    create_subscription_reminder(
        telegram_id=telegram_id,
        remind_at=datetime.now() - timedelta(minutes=1),
        days_left=2,
    )

    response = client.delete(f"/subscription-reminders/{telegram_id}")

    assert response.status_code == 204

    db = TestingSessionLocal()

    try:
        reminder = db.query(SubscriptionReminder).filter(
            SubscriptionReminder.telegram_id == telegram_id
        ).first()

        assert reminder is None

    finally:
        db.close()