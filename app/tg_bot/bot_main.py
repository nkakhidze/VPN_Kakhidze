import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.tg_bot.config.config_reader import bot_settings
from app.tg_bot.handlers.start import router as start_router
from app.tg_bot.handlers.profile import router as profile_router
from app.tg_bot.handlers.payment import router as payment_router
from app.scheduler.setup_scheduler import setup_scheduler


dp = Dispatcher()

def register_handlers():
    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(payment_router)


async def main():
    bot = Bot(token=bot_settings.bot_token)

    scheduler = setup_scheduler(bot)

    logging.basicConfig(level=logging.INFO)

    print("Проверяю токен через get_me()...")
    bot_info = await bot.get_me()
    print(f"Бот подключился: @{bot_info.username}, id={bot_info.id}")

    print("Создаю Dispatcher...")
    register_handlers()

    print("Удаляю webhook, если он был...")
    await bot.delete_webhook(drop_pending_updates=True)

    print("Запускаю polling. Теперь бот ждёт сообщения...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Бот запущен")
    asyncio.run(main())