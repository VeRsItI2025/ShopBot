from aiogram import Router, types
from aiogram.filters import Command
from keyboards.main_menu import main_menu

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "Добро пожаловать в магазин! Выберите действие:",
        reply_markup=main_menu
    )




# @router.message()
# async def get_id(message: types.Message):
#     await message.answer(f"Ваш Telegram ID: {message.from_user.id}")

# @router.message(F.photo)
# async def get_photo_id(message: types.Message):
#     await message.answer(f"file_id: {message.photo[-1].file_id}")