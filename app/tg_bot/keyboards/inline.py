from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_payment():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ Продлить VPN", callback_data="extend_subscription")]
    ])