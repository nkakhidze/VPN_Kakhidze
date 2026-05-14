from datetime import datetime

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.tg_bot.client.backend_client import (
    BackendClientError,
    create_mock_payment,
)


router = Router()


@router.callback_query(F.data == "extend_subscription")
async def extend_subscription_callback(callback: CallbackQuery):
    telegram_user = callback.from_user

    try:
        payment_result = await create_mock_payment(
            telegram_id=telegram_user.id,
        )

    except BackendClientError:
        await callback.answer(
            "Сервис временно недоступен. Попробуйте позже.",
            show_alert=True,
        )
        return

    if payment_result is None:
        await callback.answer(
            "Пользователь не найден. Сначала нажмите /start.",
            show_alert=True,
        )
        return

    payment = payment_result["payment"]
    expires_at = payment_result["subscription_expires_at"]

    expires_at_dt = datetime.fromisoformat(expires_at)
    expires_at_text = expires_at_dt.strftime("%d.%m.%Y %H:%M")

    await callback.message.answer(
        f"✅ Оплата прошла успешно.\n\n"
        f"Сумма: {payment['amount']} {payment['currency']}\n"
        f"VPN продлён на 30 дней.\n"
        f"Подписка действует до: {expires_at_text}"
    )

    await callback.answer()