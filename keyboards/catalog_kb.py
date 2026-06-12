from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def product_keyboard(product_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🛒 Добавить", callback_data=f"add_{product_id}"),
                InlineKeyboardButton(text="ℹ️ Подробнее", callback_data=f"details_{product_id}")
            ],
            [
                InlineKeyboardButton(text="⬅️ Предыдущий", callback_data="prev_product"),
                InlineKeyboardButton(text="➡️ Следующий", callback_data="next_product"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Назад к каталогу", callback_data="back_to_catalog")
            ]


            ]
        )

def price_filter_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬆️ Дешевле сначало", callback_data="filter_price_asc"),
                InlineKeyboardButton(text="⬇️ Дороже сначало", callback_data="filter_price_desc"),
            ],
            [
                InlineKeyboardButton(text="📂 Назад к катлогу", callback_data="back_to_catalog")
            ]
        ]
    )

def categories_keyboard(categories: list[str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=cat, callback_data=f"cat:{cat}")]
            for cat in categories
        ]
    )

def products_keyboard(products: list[dict]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=f"{p['name']} — {p['price']}₴", callback_data=f"details_{p['id']}")]
        for p in products
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def details_keyboard(product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад к товару", callback_data=f"back_{product_id}")],
            [InlineKeyboardButton(text="📂 Назад к каталогу", callback_data="back_to_catalog")]
        ]
    )
