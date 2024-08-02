from aiogram.fsm.state import StatesGroup, State


class PostponedState(StatesGroup):
    getting_task = State()
    task_processing = State()
