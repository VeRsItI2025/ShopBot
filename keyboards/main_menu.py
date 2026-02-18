from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Каталог")],
        [KeyboardButton(text="Корзина")],
        [KeyboardButton(text="Помощь")]
    ],
    resize_keyboard=True
)

@router.message(lambda m: m.text == "Помощь")
async def help_handler(message: types.Message):
    await message.answer(
        "Если у вас возникли вопросы напишите нашему менеджеру: @VeRsItIuS"
    )