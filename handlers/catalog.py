from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.fsm.state import StatesGroup, State


from aiogram.types import InputMediaPhoto

import db  # модуль базы данных
from keyboards.catalog_kb import product_keyboard, details_keyboard, price_filter_keyboard
from keyboards.photo_kb import details_keyboard
from services.product_service import fetch_all_products
from keyboards.admin_kb import admin_product_keyboard


router = Router()

# FSM для изменения цены
class DiscountFSM(StatesGroup):
    waiting_for_new_price = State()
    waiting_for_end_time = State()   # именно это имя


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

    # --- вот здесь добавляем проверку на скидку ---
    if product.get("status") == "Скидка" and product.get("old_price"):
        price_text = f"💰 <s>{product['old_price']}$</s> ➡️ {product['price']}$"
    else:
        price_text = f"💰 Цена: {product['price']}$"

    await callback.message.answer_photo(
        product["photos"][0],
        caption=(
            f"🏷️ {product['status']}\n" if product.get("status") == "Скидка" else ""
        ) + (
            f"📌 {product['name']}\n"
            f"{price_text}\n"
            f"📂 Категория: {product['category']}\n"
            f"ℹ️ {product['desc']}"
        ),
        reply_markup=kb,
        parse_mode="HTML"   # обязательно для <s> зачёркивания
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

    # проверка на скидку
    if product.get("status") == "Скидка" and product.get("old_price"):
        price_text = f"💰 <s>{product['old_price']}$</s> ➡️ {product['price']}$"
    else:
        price_text = f"💰 Цена: {product['price']}$"

    photos = product.get("photos") or []
    if photos:
        await callback.message.answer_photo(
            photos[0],
            caption=(
                f"🏷️ {product['status']}\n" if product.get("status") else ""
            ) + (
                f"📌 {product['name']}\n"
                f"💰 Цена: {product['price']}$\n"
                f"📂 Категория: {product['category']}\n"
                f"ℹ️ {product['desc']}"
            ),
            reply_markup=kb
        )
    else:
        await callback.message.answer(
            (
                f"🏷️ {product['status']}\n" if product.get("status") else ""
            ) + (
                f"📌 {product['name']}\n"
                f"💰 Цена: {product['price']}$\n"
                f"📂 Категория: {product['category']}\n"
                f"ℹ️ {product['desc']}\n"
                f"⚠️ Фото для этого товара отсутствует."
            ),
            reply_markup=kb
        )



# ⬅️ Предыдущий товар
@router.callback_query(lambda c: c.data == "prev_product")
async def prev_product(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    products = data.get("products", [])
    index = data.get("index", 0)

    if not products:
        await callback.message.answer("⚠️ Нет товаров для показа.")
        return

    # уменьшаем индекс (циклический просмотр)
    index = (index - 1) % len(products)
    await state.update_data(index=index)

    product = products[index]
    kb = product_keyboard(product["id"])

    # проверка на скидку
    if product.get("status") == "Скидка" and product.get("old_price"):
        price_text = f"💰 <s>{product['old_price']}$</s> ➡️ {product['price']}$"
    else:
        price_text = f"💰 Цена: {product['price']}$"

    caption = (
        f"🏷️ {product['status']}\n" if product.get("status") == "Скидка" else ""
    ) + (
        f"📌 {product['name']}\n"
        f"{price_text}\n"
        f"📂 Категория: {product['category']}\n"
        f"ℹ️ {product['desc']}"
    )

    photos = product.get("photos") or []
    if photos:
        await callback.message.answer_photo(
            photos[0],
            caption=caption,
            reply_markup=kb,
            parse_mode="HTML"
        )
    else:
        await callback.message.answer(
            caption + "\n⚠️ Фото для этого товара отсутствует.",
            reply_markup=kb,
            parse_mode="HTML"
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
            f"🔎 Характеристики:\n{product['details'] if product['details'] else 'Нет дополнительных характеристик'}"
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
        caption=(
                    f"🏷️ {product['status']}\n" if product.get("status") == "Скидка" else ""
                ) + (
                    f"📌 {product['name']}\n"
                    f"💰 Цена: {product['price']}$\n"
                    f"📂 Категория: {product['category']}\n"
                    f"ℹ️ {product['desc']}"
                ),
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



# пример показа карточки товара админу@router.message(lambda m: m.text == "/admin_product")
@router.callback_query(lambda c: c.data.startswith("admin_discounts_"))
async def show_admin_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[2])
    product = db.get_product_by_id(product_id)

    if not product:
        await callback.message.answer(f"⚠️ Товар с id={product_id} не найден.")
        return

    caption = (
        f"🏷️ {product['status']}\n" if product.get("status") == "Скидка" else ""
    ) + (
        f"📌 {product['name']}\n"
        f"💰 Цена: {product['price']}$\n"
        f"📂 Категория: {product['category']}\n"
        f"ℹ️ {product['desc']}"
    )

    photos = product.get("photos") or []
    if photos:
        await callback.message.answer_photo(
            photos[0],
            caption=caption,
            reply_markup=admin_product_keyboard(product_id, product["status"])
        )
    else:
        await callback.message.answer(
            caption + "\n⚠️ Фото отсутствует.",
            reply_markup=admin_product_keyboard(product_id, product["status"])
        )