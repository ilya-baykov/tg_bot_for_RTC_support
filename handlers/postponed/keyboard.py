from typing import List

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.CRUD.read import ClearInputTableReader
from database.models import ActionsToday, ClearInputData


class ActionInfo(CallbackData, prefix="action_info_inline_kb"):
    action_task_id: str


async def inline_deferred_tasks(actions: List[ActionsToday]):
    keyboard = InlineKeyboardBuilder()

    for action in actions:
        callback_data = ActionInfo(action_task_id=str(action.id))
        process: ClearInputData = await ClearInputTableReader.get_input_task_by_id(action.input_data_id)
        keyboard.add(InlineKeyboardButton(text=f"{process.process_name}:{process.action_description}",
                                          callback_data=callback_data.pack()))
    return keyboard.adjust(1).as_markup()


keyboard_for_report = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Выполнено"), KeyboardButton(text="Не выполнено")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
