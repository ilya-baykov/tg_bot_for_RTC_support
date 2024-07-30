from typing import List

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ProcessInfo(CallbackData, prefix="process_info_inline_kb"):
    process_name: str


async def inline_processes(employee_processes: List):
    """
    :param employee_processes: Все процессы сотрудника
    :return: Объект - inline клавиатура
    """
    keyboard = InlineKeyboardBuilder()
    for processes in employee_processes:
        callback_data = ProcessInfo(process_name=processes.name)
        keyboard.add(InlineKeyboardButton(text=f"{processes.process_name}",
                                          callback_data=callback_data.pack()))
    return keyboard.adjust(1).as_markup()
