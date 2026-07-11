from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Админ панель
def admin_menu():
    kb = [
        [InlineKeyboardButton(text="➕ Добавить товар", callback_data="admin_add")],
        [InlineKeyboardButton(text="🗑 Удалить товар", callback_data="admin_delete")],
        [InlineKeyboardButton(text="✏️ Редоктировать товар", callback_data="admin_edit")],
        [InlineKeyboardButton(text ="🔖 Скидки", callback_data="admin_discount")]
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

# Функция для добовления скидок
def admin_product_keyboard(product_id: int, current_status: str):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Удалить", callback_data=f"delete_{product_id}")],
        [InlineKeyboardButton(
            text= "💲 Скидка" if current_status != "Скидка" else "🔙 Убрать скидку",
            callback_data=f"discount_{product_id}"
        )]
    ])
    return kb