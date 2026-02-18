import types

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Клавиатру подверждения

def confirm_order_kb():
    kb = [
        [
            InlineKeyboardButton(text="Подвердить", callback_data="order_confirm"),
            InlineKeyboardButton(text="Отменить", callback_data="order_cancel"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)