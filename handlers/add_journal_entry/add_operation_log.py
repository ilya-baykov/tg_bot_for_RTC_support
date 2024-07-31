import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from database.CRUD.read import EmployeesReader, ProcessDirectoryReader
from handlers.add_journal_entry.keyboard import add_journal_log_kb, EXIT_BUTTON_TEXT, SENT_BUTTON_TEXT
from handlers.filters_general import RegisteredUser
from handlers.add_journal_entry.state import AddOperationLogState, handle_state

logger = logging.getLogger(__name__)

add_journal_router = Router()


@add_journal_router.message(F.text == EXIT_BUTTON_TEXT)
async def exit_add_operation_log(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Добавление записи в журнал эксплуатации отменено")


@add_journal_router.message(RegisteredUser(), Command('add_operation_log'))
async def command_add_operation_log(message: Message, state: FSMContext):
    """Начинаем заполнение данных для журнала эксплуатации"""
    await message.answer(
        "📝 Для добавления записи в журнал эксплуатации необходимо поочередно заполнить поля таблицы.\n\n"
        "🔄 Если какое-то поле вы заполнили неправильно, введите 'назад' для повторного заполнения.\n\n"
        "❌ Для завершения заполнения формы введите 'exit'."
    )
    await message.answer(f"Введите название процесса (без пробелов)")
    await state.set_state(AddOperationLogState.enter_process_name)


@add_journal_router.message(AddOperationLogState.enter_process_name)
async def enter_process_name(message: Message, state: FSMContext):
    """Получаем информацию по процессу и ФИО сотрудника ТП"""

    employee = await EmployeesReader().get_employee_by_telegram_id_or_username(telegram_id=str(message.from_user.id))
    process = await ProcessDirectoryReader().get_process(message.text)
    if process:
        await state.update_data({"process": process, "employee_name": employee.name})
        await message.answer("Введите описание ошибки",
                             reply_markup=add_journal_log_kb(back_button=True, exit_button=True))
        await state.set_state(AddOperationLogState.enter_error_description)
    else:
        await message.answer(f"Процесс '{message.text}' не найден. Попробуйте ввести номер RPA без пробелов.",
                             reply_markup=add_journal_log_kb(exit_button=True))
        await state.set_state(AddOperationLogState.enter_process_name)


@add_journal_router.message(AddOperationLogState.enter_error_description)
async def enter_error_description(message: Message, state: FSMContext):
    """Получаем описание ошибки"""
    answer = await handle_state(message, state, "error_description",
                                previous_state=AddOperationLogState.enter_process_name,
                                previous_message="Введите название процесса (без пробелов)",
                                next_state=AddOperationLogState.enter_error_date,
                                next_message="Введите дату ошибки")

    await message.answer(answer, reply_markup=add_journal_log_kb(back_button=True, exit_button=True))


@add_journal_router.message(AddOperationLogState.enter_error_date)
async def enter_error_date(message: Message, state: FSMContext):
    """Получаем дату ошибки"""
    answer = await handle_state(message, state, "error_date",
                                previous_state=AddOperationLogState.enter_error_description,
                                previous_message="Введите описание ошибки",
                                next_state=AddOperationLogState.enter_error_reason,
                                next_message="Введите причину ошибки")
    await message.answer(answer, reply_markup=add_journal_log_kb(back_button=True, exit_button=True))


@add_journal_router.message(AddOperationLogState.enter_error_reason)
async def enter_error_reason(message: Message, state: FSMContext):
    """Получаем причину ошибки"""
    answer = await handle_state(message, state, "error_reason",
                                previous_state=AddOperationLogState.enter_error_date,
                                previous_message="Введите дату ошибки",
                                next_state=AddOperationLogState.enter_error_solution,
                                next_message="Введите решение ошибки")
    await message.answer(answer, reply_markup=add_journal_log_kb(back_button=True, exit_button=True))


@add_journal_router.message(AddOperationLogState.enter_error_solution)
async def enter_error_solution(message: Message, state: FSMContext):
    """Получаем решение ошибки"""
    answer = await handle_state(message, state, "error_solution",
                                previous_state=AddOperationLogState.enter_error_reason,
                                previous_message="Введите причину ошибки",
                                next_state=AddOperationLogState.enter_date_solution,
                                next_message="Введите  дату решения ошибки")
    await message.answer(answer, reply_markup=add_journal_log_kb(back_button=True, exit_button=True))


@add_journal_router.message(AddOperationLogState.enter_date_solution)
async def enter_date_solution(message: Message, state: FSMContext):
    """Получаем дату решения ошибки"""
    answer = await handle_state(message, state, "decision_date",
                                previous_state=AddOperationLogState.enter_error_solution,
                                previous_message="Введите решение ошибки",
                                next_state=AddOperationLogState.enter_type_error,
                                next_message="Введите тип ошибки")
    await message.answer(answer, reply_markup=add_journal_log_kb(back_button=True, exit_button=True))


@add_journal_router.message(AddOperationLogState.enter_type_error)
async def enter_type_error(message: Message, state: FSMContext):
    """Получаем тип ошибки"""
    answer = await handle_state(message, state, "error_type",
                                previous_state=AddOperationLogState.enter_date_solution,
                                previous_message="Введите дату решения ошибки",
                                next_state=AddOperationLogState.saving_log_entry,
                                next_message="Все поля заполнены")
    await message.answer(answer, reply_markup=add_journal_log_kb(back_button=True, sent_button=True, exit_button=True))


@add_journal_router.message(AddOperationLogState.saving_log_entry)
async def save_journal_log(message: Message, state: FSMContext):
    """Получаем тип ошибки"""
    answer = await handle_state(message, state, "",
                                previous_state=AddOperationLogState.enter_type_error,
                                previous_message="Введите тип ошибки")
    if answer == SENT_BUTTON_TEXT:
        data = await state.get_data()
        await message.answer(f"{data}")
        await state.clear()
        await message.answer(f"{await state.get_data()}")
    else:
        await message.answer(answer,
                             reply_markup=add_journal_log_kb(back_button=True, sent_button=True, exit_button=True))


def register_add_operation_log_handler(dp):
    dp.include_router(add_journal_router)
