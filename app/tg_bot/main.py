import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.core.config import settings
from app.tg_bot.handlers.start import router as start_router
from app.tg_bot.handlers.profile import router as profile_router


async def main():
    logging.basicConfig(level=logging.INFO)

    print("Создаю Bot...")
    bot = Bot(token=settings.bot_token)

    print("Проверяю токен через get_me()...")
    bot_info = await bot.get_me()
    print(f"Бот подключился: @{bot_info.username}, id={bot_info.id}")

    print("Создаю Dispatcher...")
    dp = Dispatcher()

    print("Подключаю start_router...")
    dp.include_router(start_router)

    print("Подключаю profile_router...")
    dp.include_router(profile_router)

    print("Удаляю webhook, если он был...")
    await bot.delete_webhook(drop_pending_updates=True)

    print("Запускаю polling. Теперь бот ждёт сообщения...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Бот запущен")
    asyncio.run(main())