from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboards.catalog_kb import product_keyboard
import db   # модуль базы данных
from services.product_service import fetch_all_products

router = Router()


# 📦 Показать список категорий (Reply-кнопка "Каталог")
@router.message(lambda m: m.text == "Каталог")
async def show_catalog(message: types.Message):
    products = db.get_all_products()
    categories = sorted(set(p["category"] for p in products))  # уникальные категории
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=cat, callback_data=f"cat:{cat}")]
            for cat in categories
        ]
    )
    await message.answer("📂 Выберите категорию:", reply_markup=kb)


# 📂 Показать товары выбранной категории
@router.callback_query(F.data.startswith("cat:"))
async def choose_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    category = callback.data.split(":")[1]
    products = db.get_products_by_category(category)

    if not products:
        await callback.message.answer(f"⚠️ В категории {category} пока нет товара.")
        return

    shown_ids = set()  # защита от дублей
    for product in products:
        if product["id"] in shown_ids:
            continue
        shown_ids.add(product["id"])

        kb = product_keyboard(product["id"])
        await callback.message.answer_photo(
            photo=product["photo"],  # file_id или URL
            caption=(
                f"📌 {product['name']}\n"
                f"💰 Цена: {product['price']}$\n"
                f"ℹ️ {product['desc']}"
            ),
            reply_markup=kb,
        )

    # Кнопка "Назад"
    @router.callback_query(lambda c: c.data == "back_to_catalog")
    async def back_to_catalog_handler(callback: types.CallbackQuery):
        await callback.answer()
        products = fetch_all_products()
        categories = sorted(set(p["category"] for p in products))
        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text=cat, callback_data=f"cat:{cat}")]
                for cat in categories
            ]
        )
        await callback.message.answer("📂 Выберите категорию:", reply_markup=kb)

# ⬅️ Назад к списку категорий
@router.callback_query(lambda c: c.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery):
    await callback.answer()
    products = db.get_all_products()
    categories = sorted(set(p["category"] for p in products))
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=cat, callback_data=f"cat:{cat}")]
            for cat in categories
        ]
    )
    await callback.message.answer("📂 Выберите категорию:", reply_markup=kb)


# ℹ️ Подробнее о товаре
@router.callback_query(lambda c: c.data.startswith("details_"))
async def product_details(callback: types.CallbackQuery):
    await callback.answer()
    product_id = int(callback.data.split("_")[1])
    product = db.get_product_by_id(product_id)

    if not product:
        await callback.message.answer("⚠️ Товар не найден.")
        return

    kb = product_keyboard(product["id"])
    await callback.message.answer_photo(
        photo=product["photo"],
        caption=(
            f"📌 {product['name']}\n"
            f"💰 Цена: {product['price']}$\n"
            f"ℹ️ {product['desc']}"
        ),
        reply_markup=kb,
    )