from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from aiogram.types import InputMediaPhoto

import db  # модуль базы данных
from keyboards.catalog_kb import product_keyboard, details_keyboard, price_filter_keyboard
from keyboards.photo_kb import details_keyboard
from services.product_service import fetch_all_products

router = Router()


# 📦 Показать список категорий (Reply-кнопка "Каталог")
@router.message(lambda m: m.text == "Каталог")
async def show_catalog(message: types.Message):
    products = db.get_all_products()
    categories = sorted(set(p["category"] for p in products))
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

    # сохраняем список товаров и индекс
    await state.update_data(products=products, index=0)

    # предлагаем выбрать фильтр
    await callback.message.answer("🔎 Хотите отфильтровать товары по цене?", reply_markup=price_filter_keyboard())

    product = products[0]
    kb = product_keyboard(product["id"])  # тут добавим кнопку "Следующий"
    from aiogram.types import InputMediaPhoto

    await callback.message.answer_photo(
        product["photos"][0],
        caption=f"📌 {product['name']}\n💰 Цена: {product['price']}$\nℹ️ {product['desc']}",
        reply_markup=product_keyboard(product["id"])
    )


# ➡️ Следующий товар
@router.callback_query(lambda c: c.data == "next_product")
async def next_product(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    products = data.get("products", [])
    index = data.get("index", 0)

    if not products:
        await callback.message.answer("⚠️ Нет товаров для показа.")
        return

    # следующий индекс
    index = (index + 1) % len(products)  # циклический просмотр
    await state.update_data(index=index)

    product = products[index]
    kb = product_keyboard(product["id"])
    await callback.message.answer_photo(
        product["photos"][0],  # берём первое фото
        caption=f"📌 {product['name']}\n💰 Цена: {product['price']}$\nℹ️ {product['desc']}",
        reply_markup=kb
    )



# ⬅️ Преведущий товар
@router.callback_query(lambda c: c.data == "prev_product")
async def prev_product(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    products = data.get("products", [])
    index = data.get("index", 0)

    if not products:
        await callback.message.answer("⚠️ Нет товаров для показа.")
        return

    # уменьшаем индекс
    index = (index - 1) % len(products)
    await state.update_data(index=index)

    product = products[index]
    kb = product_keyboard(product["id"])
    await callback.message.answer_photo(
        product["photos"][0],  # берём первое фото
        caption=f"📌 {product['name']}\n💰 Цена: {product['price']}$\nℹ️ {product['desc']}",
        reply_markup=kb
    )



# ℹ️ Подробнее о товаре
@router.callback_query(lambda c: c.data.startswith("details_"))
async def product_details(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    product = db.get_product_by_id(product_id)

    await callback.message.edit_media(
        types.InputMediaPhoto(media=product["photos"][0])
    )
    await callback.message.edit_caption(
        caption=(
            f"📌 {product['name']} — {product['price']}$\n"
            f"Категория: {product['category']}\n"
            f"Описание: {product['desc']}\n\n"
            f"🔎 Характеристики:\n{product['details']}"
        ),
        reply_markup=details_keyboard(product_id, index=0)  # клавиатура с навигацией
    )

@router.callback_query(lambda c: c.data.startswith("photo_next_"))
async def next_photo(callback: CallbackQuery, state: FSMContext):
    product_id, index = map(int, callback.data.split("_")[2:])
    product = db.get_product_by_id(product_id)

    index = (index + 1) % len(product["photos"])
    await callback.message.edit_media(
        types.InputMediaPhoto(media=product["photos"][index])
    )
    await callback.message.edit_caption(
        caption=callback.message.caption,  # оставляем тот же текст
        reply_markup=details_keyboard(product_id, index=index)
    )

@router.callback_query(lambda c: c.data.startswith("photo_prev_"))
async def next_photo(callback: CallbackQuery, state: FSMContext):
    product_id, index = map(int, callback.data.split("_")[2:])
    product = db.get_product_by_id(product_id)

    index = (index + 1) % len(product["photos"])
    await callback.message.edit_media(
        types.InputMediaPhoto(media=product["photos"][index])
    )
    await callback.message.edit_caption(
        caption=callback.message.caption,  # оставляем тот же текст
        reply_markup=details_keyboard(product_id, index=index)
    )


# ⬅️ Назад к товару
@router.callback_query(lambda c: c.data.startswith("back_") and c.data.split("_")[1].isdigit())
async def back_to_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    product = db.get_product_by_id(product_id)

    kb = product_keyboard(product_id)
    await callback.message.edit_media(
        types.InputMediaPhoto(media=product["photos"][0])
    )
    await callback.message.edit_caption(
        caption=f"📌 {product['name']}\n💰 Цена: {product['price']}$\nℹ️ {product['desc']}",
        reply_markup=kb
    )



# ⬅️ Назад к каталогу
@router.callback_query(lambda c: c.data == "back_to_catalog")
async def back_to_catalog(callback: types.CallbackQuery):
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




@router.callback_query(lambda c: c.data == "filter_price_asc")
async def filter_price_asc(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    products = sorted(data["products"], key=lambda p: p["price"])
    await state.update_data(products=products, index=0)

    product = products[0]
    kb = product_keyboard(product["id"])
    photos = [InputMediaPhoto(media=p) for p in product["photos"]]
    await callback.message.answer_media_group(photos)

    await callback.message.answer(
        f"📌 {product['name']}\n💰 Цена: {product['price']}$\nℹ️ {product['desc']}",
        reply_markup=kb
    )


@router.callback_query(lambda c: c.data == "filter_price_desc")
async def filter_price_desc(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    products = sorted(data["products"], key=lambda p: p["price"], reverse=True)
    await state.update_data(products=products, index=0)

    product = products[0]
    kb = product_keyboard(product["id"])
    photos = [InputMediaPhoto(media=p) for p in product["photos"]]
    await callback.message.answer_media_group(photos)

    await callback.message.answer(
        f"📌 {product['name']}\n💰 Цена: {product['price']}$\nℹ️ {product['desc']}",
        reply_markup=kb
    )

