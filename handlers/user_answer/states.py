from aiogram.fsm.state import State, StatesGroup


class WaitUserResponse(StatesGroup):
    task_send = State()
    response = State()
