from aiogram.fsm.state import StatesGroup, State


class EditState(StatesGroup):
    on_edit = State()
    write_comment = State()
