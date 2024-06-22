from aiogram.fsm.state import State, StatesGroup


class UserRegistration(StatesGroup):
    input_phone = State()
