# keyboards/cart_kb.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def cart_menu(user_cart):
    buttons = []

    # Кнопки удаления по id
    for item in user_cart:
        buttons.append([
            InlineKeyboardButton(
                text=f"❌ Удалить {item['name']}",
                callback_data=f"remove_{item['id']}"
            )
        ])

    # Действия
    buttons.append([
        InlineKeyboardButton(text="🗑 Очистить", callback_data="clear_cart"),
        InlineKeyboardButton(text="✅ Оформить", callback_data="checkout"),
    ])

    # Навигация
    buttons.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_catalog")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)