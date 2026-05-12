from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.db.database import SessionLocal
from app.services.user_service import get_or_create_user
from app.services.subscription_service import get_subscription_status

router = Router()


@router.message(CommandStart())
async def start_command(message: Message):
    telegram_user = message.from_user

    if telegram_user is None:
        await message.answer("Не удалось определить пользователя Telegram.")
        return

    db = SessionLocal()

    try:
        user = get_or_create_user(
            db=db,
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
        )

        subscription_status = get_subscription_status(
            db=db,
            telegram_id=user.telegram_id,
        )

        if subscription_status.is_active:
            text = (
                f"Привет, {user.first_name or 'пользователь'}!\n\n"
                f"Ты уже зарегистрирован в VPN-сервисе.\n"
                f"Статус подписки: активна.\n"
                f"Осталось дней: {subscription_status.days_left}."
            )
        else:
            text = (
                f"Привет, {user.first_name or 'пользователь'}!\n\n"
                f"Ты зарегистрирован в VPN-сервисе.\n"
                f"Статус подписки: не активна.\n\n"
                f"Позже здесь появится покупка доступа."
            )

        await message.answer(text)

    finally:
        db.close()