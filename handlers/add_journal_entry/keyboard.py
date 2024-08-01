from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from handlers.add_journal_entry.constant_text import (BACK_BUTTON_TEXT, SKIP_BUTTON_TEXT,
                                                      SENT_BUTTON_TEXT, EXIT_BUTTON_TEXT)
from handlers.add_journal_entry.state import AddOperationLogState

# Состояния с кнопками "Назад" и "Выйти"
BACK_BUTTON_STATES = (AddOperationLogState.enter_error_description,
                      AddOperationLogState.enter_error_date,
                      AddOperationLogState.enter_error_reason,
                      AddOperationLogState.enter_error_solution,
                      AddOperationLogState.enter_date_solution,
                      AddOperationLogState.enter_ticket_OTRS,
                      AddOperationLogState.enter_virtual_machine,
                      AddOperationLogState.enter_execution_time,
                      AddOperationLogState.enter_type_error,
                      AddOperationLogState.saving_log_entry)

# Состояния с кнопками "Назад", "Выйти", "Пропустить"
SKIP_BUTTONS_STATES = (AddOperationLogState.enter_error_reason,
                       AddOperationLogState.enter_error_solution,
                       AddOperationLogState.enter_date_solution,
                       AddOperationLogState.enter_ticket_OTRS,
                       AddOperationLogState.enter_execution_time,
                       AddOperationLogState.enter_type_error)


async def add_journal_log_kb(current_state: FSMContext):
    current_state = await current_state.get_state()
    builder = ReplyKeyboardBuilder()
    adjust_param = (2,)
    if current_state in BACK_BUTTON_STATES:
        builder.button(text=BACK_BUTTON_TEXT)
    if current_state in SKIP_BUTTONS_STATES:
        builder.button(text=SKIP_BUTTON_TEXT)
    if current_state == AddOperationLogState.enter_type_error:
        builder.button(text="Инфраструктурная ошибка")
        builder.button(text="Бизнес ошибка")
        builder.button(text="Ошибка робота")
        builder.button(text="Ошибка запуска")
        adjust_param = (2, 2, 2, 1)
    if current_state == AddOperationLogState.saving_log_entry:
        builder.button(text=SENT_BUTTON_TEXT)
    builder.button(text=EXIT_BUTTON_TEXT)
    builder.adjust(*adjust_param)
    return builder.as_markup(resize_keyboard=True,
                             input_field_placeholder="Нажмите на одну из кнопок или введите текст",
                             one_time_keyboard=True)
