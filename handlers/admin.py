from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from keyboards.admin_kb import admin_menu, delete_product_kb, edit_product_kb
from states.admin_states import AddProducts, EditProducts
import db

router =Router()

ADMIN = [847895304]

@router.message(F.text == "/add")
async def show_admin_menu(message: types.Message):
    if message.from_user.id not in ADMIN:
        await message.answer("У вас нет доступа.")
        return
    await message.answer("Админ-панель", reply_markup=admin_menu())

# Добавление товара

@router.callback_query(F.data == "admin_add")
async def admin_add_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название товара:")
    await state.set_state(AddProducts.name)

@router.message(AddProducts.name)
async def add_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите категорию товара:")
    await state.set_state(AddProducts.category)

@router.message(AddProducts.category)
async def add_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("Введите цену товару:")
    await state.set_state(AddProducts.price)

@router.message(AddProducts.price)
async def add_price(message: types.Message, state: FSMContext):
    await state.update_data(price=float(message.text))
    await message.answer("Введите описание товара:")
    await state.set_state(AddProducts.desc)

@router.message(AddProducts.desc)
async def add_desc(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text)
    await message.answer("Отпрвьте фото товара:")
    await state.set_state(AddProducts.photo)

@router.message(AddProducts.photo, F.photo)
async def add_photo(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)

    data = await state.get_data()
    db.add_product(
        data["name"], data["category"], data["price"], data["desc"], data["photo"]
    )

    await message.answer("Товар добавлен!")
    await state.clear()



# Функция для редактирование товара
@router.callback_query(F.data == "admin_edit")
async def show_edit_menu(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN:
        await callback.message.answer("⛔ У вас нет доступа.")
        return

    products = db.get_all_products()
    if not products:
        await callback.message.answer("❌  базе нет товара.")
        return

    for product in products:
        await callback.message.answer(
            f"🛒 {product['name']} — {product['price']} $",
            reply_markup = edit_product_kb(product['id'], product['name'])
        )

# Запуска для редактирования конкретного товара

@router.callback_query(F.data.startswith("edit_"))
async def start_edit(callback: types.CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[1])
    await state.update_data(product_id=product_id)
    await callback.message.answer("Что хотети изменить? (имя/категорию/цену/описание/фото)")
    await state.set_state(EditProducts.choose_field)

# Выбор поля
@router.message(EditProducts.choose_field)
async def choose_field(message: types.Message, state: FSMContext):
    field = message.text.strip().lower()
    if field not in FIELD_MAP:
        await message.answer("⚠️ Неверное поле. Используйте: name/category/price/desc/photo")
    await state.update_data(field=FIELD_MAP[field])
    await message.answer(f"Введите новое значение для {field}:")
    await state.set_state(EditProducts.new_value)

# Ввод нового значения
@router.message(EditProducts.new_value)
async def set_new_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    product_id = data["product_id"]
    field = data["field"]
    value = message.text

    # Если редактировать цену - преобразуем в число

    if field == "price":
        try:
            value = float(value)
        except ValueError:
            await message.answer("⚠️ Введите число для цены.")
            return

    db.update_product(product_id, field, value)
    await message.answer("✅ Товар обновлён!")
    await state.clear()



# 🗑 Удаление товаров через кнопку в админ-панели
@router.callback_query(F.data == "admin_delete")
async def show_delete_menu(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN:
        await callback.message.answer("⛔ У вас нет доступа.")
        return

    products = db.get_all_products()
    if not products:
        await callback.message.answer("❌ В базе нет товаров.")
        return

    for product in products:
        await callback.message.answer(
            f"🛒 {product['name']} — {product['price']} $",
            reply_markup=delete_product_kb(product['id'], product['name'])
        )

# 🗑 Обработка нажатия кнопки «Удалить»
@router.callback_query(F.data.startswith("delete_"))
async def delete_product_handler(callback: types.CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    db.delete_product(product_id)
    await callback.message.edit_text("✅ Товар удалён!")
    await callback.answer()

FIELD_MAP = {
    "name": "name",
    "category": "category",
    "price": "price",
    "desc": "desc",
    "photo": "photo",
    "описание": "desc",   # если админ вводит по-русски

    "название": "name",
    "категория": "category",
    "цена": "price",
    "фото": "photo"
}