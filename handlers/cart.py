from aiogram import Router, types
from db import (
    add_to_cart,
    get_cart,
    clear_cart,
    remove_from_cart,
    calculate_total,
    get_product_by_id
)
from states.order_states import Order
from keyboards.cart_kb import cart_menu
from keyboards.catalog_kb import product_keyboard
from services.product_service import fetch_product_by_id, fetch_all_products
from aiogram.fsm.context import FSMContext

router = Router()


def build_cart_text(user_cart: list, total: int, checkout: bool = False) -> str:
    if not user_cart:
        return "🛒 Ваша корзина пуста"
    if checkout:
        return (
            f"✅ Заказ оформлен!\n\n"
            f"Товаров: {len(user_cart)}\n"
            f"Итого: {total}$\n"
            f"Мы скоро свяжемся с вами 📞"
        )
    text = "🛒 Ваша корзина:\n\n"
    for item in user_cart:
        text += f"- {item['name']} ({item['price']}$)\n"
    text += f"\n💰 Итого: {total}$"
    return text


async def send_cart(message: types.Message, user_id: int, checkout: bool = False):
    user_cart = get_cart(user_id)
    total = calculate_total(user_id)
    text = build_cart_text(user_cart, total, checkout)
    if checkout:
        await message.answer(text)
    else:
        await message.answer(text, reply_markup=cart_menu(user_cart))


# 📦 Показать корзину
@router.message(lambda m: m.text == "Корзина")
async def show_cart_handler(message: types.Message):
    await send_cart(message, message.from_user.id)


# ➕ Добавить товар в корзину
@router.callback_query(lambda c: c.data.startswith("add_"))
async def add_item_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    product_id = int(callback.data.split("_")[1])
    product = fetch_product_by_id(product_id)
    if not product:
        await callback.message.answer("⚠️ Товар не найден.")
        return
    add_to_cart(user_id, product["id"], 1)
    await callback.message.answer(f"✅ Добавлено: {product['name']}")
    await send_cart(callback.message, user_id)


# 🗑 Очистить корзину
@router.callback_query(lambda c: c.data == "clear_cart")
async def clear_cart_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    clear_cart(user_id)
    await send_cart(callback.message, user_id)


# ➖ Удалить товар из корзины
@router.callback_query(lambda c: c.data.startswith("remove_"))
async def remove_item_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    uid = int(callback.data.split("_")[1])
    service_remove_from_cart(user_id, uid)
    await send_cart(callback.message, user_id)


# ⬅️ Назад: возвращаемся к каталогу карточками
@router.callback_query(lambda c: c.data == "back_to_catalog")
async def back_to_catalog_handler(callback: types.CallbackQuery):
    products = fetch_all_products()
    for product in products:
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


# ✅ Оформить заказ
@router.callback_query(lambda c: c.data == "checkout")
async def checkout_handler(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_cart = get_cart(user_id)

    if not user_cart:
        await callback.message.answer("⚠️ Ваша корзина пуста.")
        return

    # сохраняем корзину во временные данные FSM

    # начинаем процесс оформления заказа
    await callback.message.answer("Введите ваше имя:")
    await state.set_state(Order.name)
