import enum
from typing import Dict, Any

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message


async def saving_log_entry(message: Message, state: FSMContext):
    """Сохраняем запись в журнал эксплуатации"""
    await message.answer("ГОТОВО")
    await state.clear()


class AddOperationLogState(StatesGroup):
    enter_process_name = State()
    enter_error_description = State()
    enter_error_date = State()
    enter_error_reason = State()
    enter_error_solution = State()
    enter_date_solution = State()
    enter_type_error = State()
    saving_log_entry = State()


async def handle_state(message: Message, state: FSMContext, data_key: str,
                       previous_state: State,
                       previous_message: str,
                       next_state: State | None = None,
                       next_message: str = "",
                       ) -> str:
    """
    Обновляет данные в state; устанавливает нужный state в зависимости от сообщения пользователя
    :param message:  сообщение от пользователя
    :param state:    машина состояний
    :param data_key: поле для обновления словаря данных в state

    :param previous_state: текущее состояние пользователя
    :param previous_message: Текст сообщения для предыдущего состояния

    :param next_state: следующее состояние пользователя
    :param next_message: Текст сообщения для следующего состояния

    :return:  Текст ответа для пользователя
    """
    if message.text.lower() != "назад":
        await state.update_data({data_key: message.text})
        if next_state:

            if next_state != AddOperationLogState.saving_log_entry:
                await state.set_state(next_state)
            else:
                await saving_log_entry(message, state)

            return next_message

    else:
        await state.set_state(previous_state)
        return previous_message
