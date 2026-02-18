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