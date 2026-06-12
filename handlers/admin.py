from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from keyboards.admin_kb import admin_menu, delete_product_kb, edit_product_kb
from states.admin_states import AddProducts, EditProducts
import db
from aiogram.types import ContentType

router = Router()
ADMIN_IDS = [847895304]  # список админов

# --- Проверка доступа ---
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# --- Вход в админ-панель ---
@router.message(F.text == "/admin")
async def show_admin_menu(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа.")
        return
    await message.answer("📋 Админ-панель", reply_markup=admin_menu())

# --- Добавление товара ---
@router.callback_query(F.data == "admin_add")
async def admin_add_start(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.message.answer("⛔ У вас нет доступа.")
        return
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
    await message.answer("Введите цену товара:")
    await state.set_state(AddProducts.price)

@router.message(AddProducts.price)
async def add_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("⚠️ Введите число для цены.")
        return
    await state.update_data(price=price)
    await message.answer("Введите описание товара:")
    await state.set_state(AddProducts.desc)

@router.message(AddProducts.desc)
async def add_desc(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text)
    await message.answer("Отправьте фото товара:")
    await state.set_state(AddProducts.photo)

# обработка фото
@router.message(AddProducts.photo, F.content_type == ContentType.PHOTO)
async def add_photo(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    data = await state.get_data()
    photos = data.get("photos", [])
    photos.append(photo_id)
    await state.update_data(photos=photos)

    # переводим на ввод подробных характеристик
    await message.answer("Введите подробные характеристики товара:")
    await state.set_state(AddProducts.details)

# обработка «подробнее»
@router.message(AddProducts.details)
async def add_details(message: types.Message, state: FSMContext):
    await state.update_data(details=message.text)

    data = await state.get_data()
    db.add_product(
        data["name"],
        data["category"],
        data["price"],
        data["desc"],
        data["photos"],
        data["details"]   # новое поле
    )

    await message.answer("✅ Товар добавлен с подробными характеристиками!")
    await state.clear()



# --- Редактирование товара ---
@router.callback_query(F.data == "admin_edit")
async def show_edit_menu(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.message.answer("⛔ У вас нет доступа.")
        return

    products = db.get_all_products()
    if not products:
        await callback.message.answer("❌ В базе нет товаров.")
        return

    for product in products:
        await callback.message.answer(
            f"🛒 {product['name']} — {product['price']} $",
            reply_markup=edit_product_kb(product['id'], product['name'])
        )

@router.callback_query(F.data.startswith("edit_"))
async def start_edit(callback: types.CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[1])
    await state.update_data(product_id=product_id)
    await callback.message.answer("Что хотите изменить? (name/category/price/desc/photo)")
    await state.set_state(EditProducts.choose_field)

@router.message(EditProducts.choose_field)
async def choose_field(message: types.Message, state: FSMContext):
    field = message.text.strip().lower()
    if field not in FIELD_MAP:
        await message.answer("⚠️ Неверное поле. Используйте: name/category/price/desc/photo")
        return
    await state.update_data(field=FIELD_MAP[field])
    await message.answer(f"Введите новое значение для {field}:")
    await state.set_state(EditProducts.new_value)

@router.message(EditProducts.new_value)
async def set_new_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    product_id = data["product_id"]
    field = data["field"]
    value = message.text

    if field == "price":
        try:
            value = float(value)
        except ValueError:
            await message.answer("⚠️ Введите число для цены.")
            return

    db.update_product(product_id, field, value)
    await message.answer("✅ Товар обновлён!")
    await state.clear()


# Хендлер для кнопки "Подробнее"
@router.callback_query(F.data.startswith("info_"))
async def show_details(callback: types.CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    product = db.get_product_by_id(product_id)

    if not product:
        await callback.message.answer("❌ Товар не найден.")
        await callback.answer()
        return

    details_text = product['details'] if product['details'] else "Нет дополнительных характеристик"

    text = (
        f"📱 {product['name']} — {product['price']} $\n"
        f"Категория: {product['category']}\n"
        f"Описание: {product['desc']}\n\n"
        f"🔎 Подробнее:\n{details_text}"
    )

    if product["photos"]:
        await callback.message.answer_photo(product["photos"][0], caption=text)
    else:
        await callback.message.answer(text)

    await callback.answer()  # закрываем "часики"



# --- Удаление товара ---
@router.callback_query(F.data == "admin_delete")
async def show_delete_menu(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
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

@router.callback_query(F.data.startswith("delete_"))
async def delete_product_handler(callback: types.CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    db.delete_product(product_id)
    await callback.message.edit_text("✅ Товар удалён!")
    await callback.answer()

# --- Словарь полей ---
FIELD_MAP = {
    "name": "name",
    "category": "category",
    "price": "price",
    "desc": "desc",
    "photos": "photos",
    "описание": "desc",
    "название": "name",
    "категория": "category",
    "цена": "price",
    "фото": "photos"
}
