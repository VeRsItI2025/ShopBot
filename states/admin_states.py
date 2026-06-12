from aiogram.fsm.state import StatesGroup, State

class AddProducts(StatesGroup):
    name = State()
    category = State()
    price = State()
    desc = State()
    photo = State()
    details = State()

class EditProducts(StatesGroup):
    choose_field = State()
    new_value = State()

