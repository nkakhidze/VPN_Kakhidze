from datetime import datetime

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.tg_bot.client.backend_client import (
    BackendClientError,
    extend_subscription,
)


router = Router()


@router.callback_query(F.data == "extend_subscription")
async def extend_subscription_callback(callback: CallbackQuery):
    telegram_user = callback.from_user

    if telegram_user is None:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        return

    try:
        user = await extend_subscription(telegram_id=telegram_user.id)

    except BackendClientError:
        await callback.answer(
            "Сервис временно недоступен. Попробуйте позже.",
            show_alert=True,
        )
        return

    if user is None:
        await callback.answer(
            "Пользователь не найден. Сначала нажмите /start.",
            show_alert=True,
        )
        return

    expires_at = user["subscription_expires_at"]

    if expires_at is not None:
        expires_at_dt = datetime.fromisoformat(expires_at)
        expires_at_text = expires_at_dt.strftime("%d.%m.%Y %H:%M")
    else:
        expires_at_text = "неизвестно"

    await callback.message.answer(
        f"✅ VPN продлён на 30 дней.\n\n"
        f"Подписка действует до: {expires_at_text}"
    )

    await callback.answer()