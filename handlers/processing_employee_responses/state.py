from aiogram.fsm.state import State, StatesGroup


class UserResponse(StatesGroup):
    comment = State()
