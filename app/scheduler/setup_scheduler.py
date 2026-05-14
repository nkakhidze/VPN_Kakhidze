import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.scheduler.general import (
    rebuild_subscription_reminders_job,
    send_due_subscription_reminders_job,
)


logger = logging.getLogger(__name__)


def setup_scheduler(bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    scheduler.add_job(
        rebuild_subscription_reminders_job,
        trigger=CronTrigger(hour=1, minute=0),
        # trigger=CronTrigger(second=10),
        id="rebuild_subscription_reminders",
        name="Пересборка очереди напоминаний о подписке",
        replace_existing=True,
    )

    scheduler.add_job(
        send_due_subscription_reminders_job,
        trigger=CronTrigger(minute="5"),
        # trigger=CronTrigger(second=20),
        args=[bot],
        id="send_due_subscription_reminders",
        name="Отправка наступивших напоминаний о подписке",
        replace_existing=True,
    )

    scheduler.start()

    logger.info("[SCHEDULER] Планировщик запущен.")

    return scheduler