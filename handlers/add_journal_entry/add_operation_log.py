import logging
from enum import Enum

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.CRUD.read import EmployeesReader, ProcessDirectoryReader, SchedulerTasksReader
from database.CRUD.сreate import OperationLogCreator
from database.enums import ActionStatus
from handlers.add_journal_entry.constant_text import EXIT_BUTTON_TEXT, SENT_BUTTON_TEXT
from handlers.add_journal_entry.keyboard import add_journal_log_kb
from handlers.add_journal_entry.state import AddOperationLogState, handle_state
from handlers.filters_general import RegisteredUser
from utility.ActionManager import ActionManager
from run_app.main_objects import scheduler
from utility.sheduler_functions import pause_scheduler_task, resume_scheduler_task

logger = logging.getLogger(__name__)

add_journal_router = Router()


class ErrorTypes(Enum):
    ROBOT_ERROR = "Ошибка робота (плохая отказоустойчивость, невыполнение действий ТЗ, несвоевременная остановка))"
    STARTUP_ERROR = "Ошибка запуска (Проблемы ВМ, оркестратора, координатора)	"
    BUSINESS_ERROR = "Бизнес ошибка (входные данные, пользователь, изменение БП)"
    INFRASTRUCTURE_ERROR = "Инфраструктурная ошибка (сбой систем, доступов, серверов)"
    NO_VALUE = ""

    @classmethod
    def get_full_error_type(cls, description: str | None):
        if description:
            for error_type in cls:
                if description in error_type.value:
                    return error_type.value
        return None


@add_journal_router.message(F.text == EXIT_BUTTON_TEXT)
async def exit_add_operation_log(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Добавление записи в журнал эксплуатации отменено")


@add_journal_router.message(RegisteredUser(), Command('add_operation_log'))
async def command_add_operation_log(message: Message, state: FSMContext):
    """Начинаем заполнение данных для журнала эксплуатации"""
    employee = await EmployeesReader().get_employee_by_telegram_id_or_username(telegram_id=str(message.from_user.id))

    # Ставим действие планировщика на паузу
    task_in_scheduler = await SchedulerTasksReader().get_last_task_by_employee(employee_id=employee.id)
    await pause_scheduler_task(task_in_scheduler)

    await message.answer(
        "📝 Для добавления записи в журнал эксплуатации необходимо поочередно заполнить поля таблицы.\n\n"
        "🔄 Если какое-то поле вы заполнили неправильно, нажмите клавишу 'назад' для повторного заполнения.\n\n"
        "❌ Для завершения заполнения формы нажмите клавишу 'Выход'."
    )
    await state.set_state(AddOperationLogState.enter_process_name)
    await message.answer(f"Введите название процесса (без пробелов)")

    if task_in_scheduler:
        await state.update_data({"scheduler_task_id": task_in_scheduler.id})
    await state.update_data({"employee_name": employee.name})


@add_journal_router.message(AddOperationLogState.enter_process_name)
async def enter_process_name(message: Message, state: FSMContext):
    """Получаем информацию по процессу и ФИО сотрудника ТП"""

    process = await ProcessDirectoryReader().get_process(message.text)
    if process:
        await state.update_data({"process": process})
        await state.set_state(AddOperationLogState.enter_error_description)
        await message.answer("Введите описание ошибки",
                             reply_markup=await add_journal_log_kb(state))
    else:
        similar_process = await ProcessDirectoryReader().get_similar_process(message.text)
        if similar_process:
            await message.answer(
                f"Процесс '{message.text}' не найден."
                f"\nВозможно, вы имели в виду '{similar_process}'? "
                f"\nПопробуйте ввести номер RPA еще раз.",
                reply_markup=await add_journal_log_kb(state))
        else:
            await message.answer(f"Процесс '{message.text}' не найден.\nПопробуйте ввести номер RPA без пробелов.",
                                 reply_markup=await add_journal_log_kb(state))


@add_journal_router.message(AddOperationLogState.enter_error_description)
async def enter_error_description(message: Message, state: FSMContext):
    """Получаем описание ошибки"""
    answer = await handle_state(message, state, "error_description",
                                previous_state=AddOperationLogState.enter_process_name,
                                previous_message="Введите название процесса (без пробелов)",
                                next_state=AddOperationLogState.enter_error_date,
                                next_message="Введите дату ошибки")

    await message.answer(answer, reply_markup=await add_journal_log_kb(state))


@add_journal_router.message(AddOperationLogState.enter_error_date)
async def enter_error_date(message: Message, state: FSMContext):
    """Получаем дату ошибки"""
    answer = await handle_state(message, state, "error_date",
                                previous_state=AddOperationLogState.enter_error_description,
                                previous_message="Введите описание ошибки",
                                next_state=AddOperationLogState.enter_error_reason,
                                next_message="Введите причину ошибки")
    await message.answer(answer, reply_markup=await add_journal_log_kb(state))


@add_journal_router.message(AddOperationLogState.enter_error_reason)
async def enter_error_reason(message: Message, state: FSMContext):
    """Получаем причину ошибки"""
    answer = await handle_state(message, state, "error_reason",
                                previous_state=AddOperationLogState.enter_error_date,
                                previous_message="Введите дату ошибки",
                                next_state=AddOperationLogState.enter_error_solution,
                                next_message="Введите решение ошибки")
    await message.answer(answer, reply_markup=await add_journal_log_kb(state))


@add_journal_router.message(AddOperationLogState.enter_error_solution)
async def enter_error_solution(message: Message, state: FSMContext):
    """Получаем решение ошибки"""
    answer = await handle_state(message, state, "error_solution",
                                previous_state=AddOperationLogState.enter_error_reason,
                                previous_message="Введите причину ошибки",
                                next_state=AddOperationLogState.enter_date_solution,
                                next_message="Введите  дату решения ошибки")
    await message.answer(answer, reply_markup=await add_journal_log_kb(state))


@add_journal_router.message(AddOperationLogState.enter_date_solution)
async def enter_date_solution(message: Message, state: FSMContext):
    """Получаем дату решения ошибки"""
    answer = await handle_state(message, state, "decision_date",
                                previous_state=AddOperationLogState.enter_error_solution,
                                previous_message="Введите решение ошибки",
                                next_state=AddOperationLogState.enter_ticket_OTRS,
                                next_message="Введите тикет в OTRS")
    await message.answer(answer, reply_markup=await add_journal_log_kb(state))


@add_journal_router.message(AddOperationLogState.enter_ticket_OTRS)
async def enter_ticket_OTRS(message: Message, state: FSMContext):
    """Получаем Тикет в OTRS"""
    answer = await handle_state(message, state, "OTRS_ticket",
                                previous_state=AddOperationLogState.enter_date_solution,
                                previous_message="Введите дату решения ошибки",
                                next_state=AddOperationLogState.enter_virtual_machine,
                                next_message="Введите номер ВМ")

    await message.answer(answer, reply_markup=await add_journal_log_kb(state))


@add_journal_router.message(AddOperationLogState.enter_virtual_machine)
async def enter_virtual_machine(message: Message, state: FSMContext):
    """Получаем номер ВМ"""
    answer = await handle_state(message, state, "virtual_machine",
                                previous_state=AddOperationLogState.enter_ticket_OTRS,
                                previous_message="Введите тикет в OTRS",
                                next_state=AddOperationLogState.enter_execution_time,
                                next_message="Введите время выполнения,ч")
    await message.answer(answer, reply_markup=await add_journal_log_kb(state))


@add_journal_router.message(AddOperationLogState.enter_execution_time)
async def enter_execution_time(message: Message, state: FSMContext):
    """Получаем время выполнения (ч)"""
    answer = await handle_state(message, state, "execution_time",
                                previous_state=AddOperationLogState.enter_virtual_machine,
                                previous_message="Введите номер ВМ",
                                next_state=AddOperationLogState.enter_type_error,
                                next_message="Введите тип ошибки")
    await message.answer(answer, reply_markup=await add_journal_log_kb(state))


@add_journal_router.message(AddOperationLogState.enter_type_error)
async def enter_type_error(message: Message, state: FSMContext):
    """Получаем тип ошибки"""
    answer = await handle_state(message, state, "error_type",
                                previous_state=AddOperationLogState.enter_date_solution,
                                previous_message="Введите дату решения ошибки",
                                next_state=AddOperationLogState.saving_log_entry,
                                next_message="Все поля заполнены")
    await message.answer(answer, reply_markup=await add_journal_log_kb(state))


@add_journal_router.message(AddOperationLogState.saving_log_entry)
async def save_journal_log(message: Message, state: FSMContext):
    """Получаем тип ошибки"""
    answer = await handle_state(message, state, "",
                                previous_state=AddOperationLogState.enter_type_error,
                                previous_message="Введите тип ошибки")
    if answer == SENT_BUTTON_TEXT:

        data = await state.get_data()
        try:
            await OperationLogCreator.create_new_log(
                process_name=data["process"].process_name,  # Номер RPA
                employee_name=data["employee_name"],  # Имя сотрудника, отвечающего за процесс
                error_description=data["error_description"],  # Описание ошибки
                error_date=data["error_date"],  # Дата ошибки в произвольной форме
                error_reason=data["error_reason"],  # Причина ошибки
                error_solution=data["error_solution"],  # Решение ошибки
                error_type=ErrorTypes.get_full_error_type(data["error_type"]),  # Один из вариантов типа ошибок
                developer=data["process"].developer,  # Разработчик, отвечающий за процесс
                jira_link=data["process"].jira_link,  # Ссылка на робота в Jira
                decision_date=data["decision_date"],  # Дата устранения ошибки в произвольной форме
                jira_issue=data["process"].jira_issue,  # Ссылка на задачу в Jira
                virtual_machine=data["virtual_machine"],  # Номер виртуальной машины
                execution_time=data["execution_time"],  # Время выполнения в ч.
                OTRS_ticket=data["OTRS_ticket"]  # Тикет в OTRS
            )
            await message.answer(f"Запись успешно добавлена в журнал эксплуатации")
            logger.info(f"Запись : {data['process'].process_name} была успешно добавлена в журнал эксплуатации")
            if data.get("scheduler_task_id"):
                await resume_scheduler_task(data["scheduler_task_id"])

        except Exception as e:
            await message.answer(f"При добавлении записи в журнал эксплуатации произошла неизвестная ошибка")
            logger.info(
                f"При добавлении записи: {data['process'].process_name} в журнал эксплуатации "
                f"произошла ошибка {e}")
        finally:
            await state.clear()
    else:
        await message.answer(answer, reply_markup=await add_journal_log_kb(state))


def register_add_operation_log_handler(dp):
    dp.include_router(add_journal_router)
