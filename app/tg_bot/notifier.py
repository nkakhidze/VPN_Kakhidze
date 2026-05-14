from app.tg_bot.keyboards.inline import get_payment


async def send_subscription_reminder(
    bot,
    telegram_id: int,
    first_name: str | None,
    days_left: int,
):
    name_part = f"{first_name}, " if first_name else ""

    text = (
        f"{name_part}доброго дня!\n\n"
        f"Осталось *{days_left} дн.* активного пользования VPN.\n\n"
        f"Чтобы продлить использование, нажмите на кнопку ниже :)"
    )

    await bot.send_message(
        telegram_id,
        text,
        reply_markup=get_payment(),
    )