from sqlalchemy.orm import Session

from app.db.models import User


DEFAULT_TIMEZONE = "Europe/Moscow"

def get_user_by_telegram_id(db: Session, telegram_id: int) -> User | None:
    return db.query(User).filter(
        User.telegram_id == telegram_id
    ).first()


def get_or_create_user(
    db: Session,
    telegram_id: int,
    username: str | None,
    first_name: str | None,
    timezone: str = DEFAULT_TIMEZONE,
) -> User:
    user = get_user_by_telegram_id(db, telegram_id)

    if user:
        user.username = username
        user.first_name = first_name

        db.commit()
        db.refresh(user)

        return user

    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        timezone=timezone,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user