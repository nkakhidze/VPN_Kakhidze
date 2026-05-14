from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.tg_bot.client.backend_client import (
    BackendClientError,
    create_user,
    get_subscription_status,
)
from app.tg_bot.keyboards.inline import get_payment


router = Router()


@router.message(CommandStart())
async def start_command(message: Message):
    telegram_user = message.from_user

    if telegram_user is None:
        await message.answer("Не удалось определить пользователя Telegram.")
        return

    try:
        user = await create_user(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
        )

        subscription_status = await get_subscription_status(
            telegram_id=telegram_user.id,
        )

    except BackendClientError:
        await message.answer(
            "Сервис временно недоступен. Попробуйте чуть позже."
        )
        return

    if subscription_status is None:
        await message.answer(
            "Не удалось получить статус подписки. Попробуйте позже."
        )
        return

    first_name = user.get("first_name") or "пользователь"

    if subscription_status["is_active"]:
        text = (
            f"Привет, {first_name}!\n\n"
            f"Ты уже зарегистрирован в VPN-сервисе.\n"
            f"Статус подписки: активна.\n"
            f"Осталось дней: {subscription_status['days_left']}."
        )
        await message.answer(text)
    else:
        text = (
            f"Привет, {first_name}!\n\n"
            f"Ты зарегистрирован в VPN-сервисе.\n"
            f"Статус подписки: не активна.\n\n"
            f"Позже здесь появится покупка доступа."
        )
        await message.answer(text, reply_markup=get_payment())