from aiogram import Router, types, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.orders_kb import confirm_order_kb
from states.order_states import Order
import db

router = Router()
ADMIN = [847895304]

# 📌 Клавиатура для админа (статусы заказа)
def admin_order_kb(order_id: int):
    kb = [
        [
            InlineKeyboardButton(text="✅ В обработку", callback_data=f"order_process_{order_id}"),
            InlineKeyboardButton(text="📦 Доставлен", callback_data=f"order_done_{order_id}"),
            InlineKeyboardButton(text="❌ Отменить", callback_data=f"order_cancel_{order_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# 📌 Ввод имени
@router.message(Order.name)
async def order_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите ваш телефон:")
    await state.set_state(Order.phone)

# 📌 Ввод телефона
@router.message(Order.phone)
async def order_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Подтвердите заказ:", reply_markup=confirm_order_kb())
    await state.set_state(Order.confirm)

# 📌 Подтверждение заказа через кнопку
@router.callback_query(F.data == "order_confirm")
async def confirm_order(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()

    # Берём корзину из базы
    user_cart = db.get_cart(callback.from_user.id)
    if not user_cart:
        await callback.message.answer("⚠️ Ваша корзина пуста.")
        return

    order_id = db.save_order(
        user_id=callback.from_user.id,
        name=data["name"],
        phone=data["phone"],
        cart=user_cart,
    )

    total = sum(item["price"] for item in user_cart)
    order_text = (
        f"🛒 Новый заказ!\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📞 Телефон: {data['phone']}\n\n"
        f"Товары:\n" +
        "\n".join([f"- {item['name']} ({item['price']}$)" for item in user_cart]) +
        f"\n\n💰 Итого: {total} $"
    )

    # Отправляем админу
    for admin_id in ADMIN:
        await bot.send_message(admin_id, order_text, reply_markup=admin_order_kb(order_id))

    # Отправляем клиенту
    await callback.message.answer("✅ Заказ оформлен!\n"
                                  f"Товаров: {len(user_cart)}\n"
                                  f"Итого: {total}$\n"
                                  "Мы скоро свяжемся с вами 📞")

    # 📌 Теперь очищаем корзину
    db.clear_cart(callback.from_user.id)

    await state.clear()
    await callback.answer()


# 📌 Отмена заказа клиентом
@router.callback_query(F.data == "order_cancel")
async def cancel_order(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("❌ Заказ отменён.")
    await callback.answer()

# 📌 Изменение статуса заказа админом
@router.callback_query(F.data.startswith("order_process_"))
async def process_order(callback: types.CallbackQuery, bot: Bot):
    order_id = int(callback.data.split("_")[2])
    db.update_order_status(order_id, "В обработке")

    # уведомляем админа
    await callback.message.answer("🔄 Заказ переведён в статус 'В обработке'")
    # уведомляем клиента
    order = db.get_order_by_id(order_id)
    if order:
        await bot.send_message(order["user_id"], "📢 Ваш заказ переведён в статус: В обработке")

    await callback.answer()

@router.callback_query(F.data.startswith("order_done_"))
async def done_order(callback: types.CallbackQuery, bot: Bot):
    order_id = int(callback.data.split("_")[2])
    db.update_order_status(order_id, "Доставлен")

    await callback.message.answer("📦 Заказ отмечен как 'Доставлен'")
    order = db.get_order_by_id(order_id)
    if order:
        await bot.send_message(order["user_id"], "📢 Ваш заказ доставлен!")

    await callback.answer()

@router.callback_query(F.data.startswith("order_cancel_"))
async def cancel_order_admin(callback: types.CallbackQuery, bot: Bot):
    order_id = int(callback.data.split("_")[2])
    db.update_order_status(order_id, "Отменён")

    await callback.message.answer("❌ Заказ отменён")
    order = db.get_order_by_id(order_id)
    if order:
        await bot.send_message(order["user_id"], "📢 Ваш заказ был отменён.")

    await callback.answer()

