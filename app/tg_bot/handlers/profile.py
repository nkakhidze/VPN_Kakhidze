from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message

from app.db.database import SessionLocal
from app.services.user_service import get_or_create_user
from app.services.subscription_service import get_subscription_status

router = Router()


@router.message(Command("profile"))
async def cmd_profile(message: types.Message):
    telegram_user = message.from_user

    if telegram_user is None:
        await message.answer("Не удалось определить пользователя Telegram.")
        return

    db = SessionLocal()
    await message.answer("Это ваш профиль!")
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
                f"Статус подписки: активна.\n"
                f"Осталось дней: {subscription_status.days_left}."
            )
        else:
            text = (
                f"Статус подписки: не активна.\n\n"
                f"Лошара, активируй подписку"
            )

        await message.answer(text)

    finally:
        db.close()