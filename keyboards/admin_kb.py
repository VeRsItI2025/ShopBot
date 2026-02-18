from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_menu():
    kb = [
        [InlineKeyboardButton(text="➕ Добавить товар", callback_data="admin_add")],
        [InlineKeyboardButton(text="🗑 Удалить товар", callback_data="admin_delete")],
        [InlineKeyboardButton(text="✏️ Редоктировать товар", callback_data="admin_edit")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# Функция для удалени товара из каталога
def delete_product_kb(product_id: int, product_name: str):
    kb = [
        [InlineKeyboardButton(
            text=f"Удалить {product_name}",
            callback_data=f"delete_{product_id}"
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# Функция для редоктирования товара
def edit_product_kb(product_id: int, product_name: str):
    kb = [
        [InlineKeyboardButton(
            text=f"Редактировать {product_name}",
            callback_data=f"edit_{product_id}"
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
