import logging

from app.tg_bot.client.backend_client import (
    BackendClientError,
    delete_subscription_reminder,
    get_due_subscription_reminders,
    rebuild_subscription_reminders,
)
from app.tg_bot.notifier import send_subscription_reminder


logger = logging.getLogger(__name__)


async def rebuild_subscription_reminders_job():
    try:
        result = await rebuild_subscription_reminders()

        logger.info(
            "Очередь напоминаний пересобрана. Удалено: %s, создано: %s",
            result["deleted_count"],
            result["created_count"],
        )

    except BackendClientError as e:
        logger.exception("Ошибка при пересборке очереди напоминаний: %s", e)


async def send_due_subscription_reminders_job(bot):
    try:
        reminders = await get_due_subscription_reminders()

    except BackendClientError as e:
        logger.exception("Ошибка при получении напоминаний: %s", e)
        return

    for reminder in reminders:
        telegram_id = reminder["telegram_id"]
        first_name = reminder.get("first_name")
        days_left = reminder["days_left"]

        try:
            await send_subscription_reminder(
                bot=bot,
                telegram_id=telegram_id,
                first_name=first_name,
                days_left=days_left,
            )

            await delete_subscription_reminder(telegram_id)

            logger.info(
                "Напоминание отправлено и удалено из очереди: telegram_id=%s",
                telegram_id,
            )

        except Exception as e:
            logger.exception(
                "Не удалось отправить напоминание telegram_id=%s: %s",
                telegram_id,
                e,
            )