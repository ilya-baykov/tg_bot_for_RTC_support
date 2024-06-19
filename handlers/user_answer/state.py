from aiogram.fsm.state import State, StatesGroup


class UserResponse(StatesGroup):
    wait_message = State()
    comment = State()
