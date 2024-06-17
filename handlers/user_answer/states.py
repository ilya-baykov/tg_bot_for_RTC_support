from aiogram.fsm.state import State, StatesGroup


class UserResponse(StatesGroup):
    task_send = State()
    response = State()
    comment = State()
