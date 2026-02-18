from aiogram.fsm.state import StatesGroup, State

class Order(StatesGroup):
    name = State()
    phone = State()
    confirm = State()