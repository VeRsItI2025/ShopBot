from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def details_keyboard(product_id: int, index: int = 0):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️ Предыдущее фото", callback_data=f"photo_prev_{product_id}_{index}"),
            InlineKeyboardButton(text="➡️ Следующее фото", callback_data=f"photo_next_{product_id}_{index}")
        ],
        [InlineKeyboardButton(text= "🔙 Назад", callback_data=f"back_{product_id}")]
    ])
    return kb