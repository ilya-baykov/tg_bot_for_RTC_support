from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from handlers.add_journal_entry.keyboard import BACK_BUTTON_TEXT, SENT_BUTTON_TEXT, SKIP_BUTTON_TEXT


async def saving_log_entry(message: Message, state: FSMContext):
    """Сохраняем запись в журнал эксплуатации"""
    await message.answer("ГОТОВО")
    await state.clear()


class AddOperationLogState(StatesGroup):
    enter_process_name = State()
    enter_error_description = State()
    enter_error_date = State()
    enter_ticket_OTRS = State()
    enter_virtual_machine = State()
    enter_execution_time = State()
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
    if message.text == BACK_BUTTON_TEXT:
        await state.set_state(previous_state)
        return previous_message
    elif message.text == SENT_BUTTON_TEXT:
        return SENT_BUTTON_TEXT
    else:
        await state.update_data({data_key: message.text.replace(SKIP_BUTTON_TEXT, "")})
        if next_state:
            await state.set_state(next_state)
            return next_message
