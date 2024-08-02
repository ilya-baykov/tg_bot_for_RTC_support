import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.CRUD.read import ClearInputTableReader, ProcessDirectoryReader, SchedulerTasksReader
from database.CRUD.сreate import actions_today_reader
from database.models import ClearInputData, ProcessDirectory
from handlers.add_journal_entry.state import AddOperationLogState
from handlers.filters_general import RegisteredUser
from handlers.processing_employee_responses.keyboard import yes_or_no_keyboard
from middlewares.ThrottlingMiddleware import ThrottlingMiddleware
from database.enums import FinalStatus, ActionStatus
from handlers.processing_employee_responses.state import UserResponse
from run_app.main_objects import scheduler
from sent_task_to_emploeyee.sending_messages import add_task_scheduler
from utility.ActionManager import ActionManager, AfterFillingReportReturn, actions_today_updater
from utility.sheduler_functions import pause_scheduler_task

logger = logging.getLogger(__name__)

user_answer = Router()
user_answer.message.middleware(ThrottlingMiddleware(limit=1))


@user_answer.message(RegisteredUser(), F.text == "Отложить")
async def user_response(message: Message, state: FSMContext):
    """Изменяет статус задачи на ActionStatus.postponed """

    employee, sent_process = await ActionManager.check_user_response(str(message.from_user.id))

    # Изменяем статус действия на "Отложено"
    await actions_today_updater.update_status(sent_process, ActionStatus.postponed)

    # Если есть следующее действие на отправку - изменяем статус следующего действия на "Ожидает отправку"
    next_sent_processes = await actions_today_reader.get_queued_to_be_added_actions_by_employee_id(employee.id)
    if next_sent_processes:
        next_process = next_sent_processes[0]
        logging.info(f"Следующее действие на отправку: {next_process.id}")

        await actions_today_updater.update_status(next_process, ActionStatus.waiting_to_be_sent)
        await add_task_scheduler(action_task=next_process)


@user_answer.message(RegisteredUser(), F.text == "Выполнено")
async def user_response(message: Message, state: FSMContext):
    """Сохраняет запись в результирующей таблице со статусом FinalStatus.successfully"""
    result: AfterFillingReportReturn = await ActionManager.filling_out_report(
        user_telegram_id=str(message.from_user.id),
        status=FinalStatus.successfully,
        comment="")
    await message.answer(result.message)


@user_answer.message(RegisteredUser(), F.text == "Не выполнено")
async def user_response(message: Message, state: FSMContext):
    await state.set_state(UserResponse.comment)
    await message.answer("Напиши комментарий")


@user_answer.message(F.text == "Да", UserResponse.comment)
async def start_add_journal_entry(message: Message, state: FSMContext):
    state_data = await state.get_data()
    result: AfterFillingReportReturn = await ActionManager.filling_out_report(
        user_telegram_id=str(message.from_user.id),
        status=FinalStatus.failed,
        comment=state_data["comment"])
    # Ставим действие планировщика на паузу
    task_in_scheduler = await SchedulerTasksReader().get_last_task_by_employee(employee_id=result.employee.id)
    await pause_scheduler_task(task_in_scheduler)
    if task_in_scheduler:
        await state.update_data({"scheduler_task_id": task_in_scheduler.id})
    await message.answer(result.message)

    process: ClearInputData = await ClearInputTableReader.get_input_task_by_id(result.sent_process.input_data_id)
    process: ProcessDirectory = await ProcessDirectoryReader().get_process(process.process_name.strip())
    await state.update_data({"employee_name": result.employee.name, "process": process})
    await message.answer("Введите описание ошибки")
    await state.set_state(AddOperationLogState.enter_error_description)


@user_answer.message(F.text == "Нет", UserResponse.comment)
async def end_report_entry(message: Message, state: FSMContext):
    state_data = await state.get_data()
    result: AfterFillingReportReturn = await ActionManager.filling_out_report(
        user_telegram_id=str(message.from_user.id),
        status=FinalStatus.failed,
        comment=state_data["comment"])
    await message.answer(result.message)
    await state.clear()


@user_answer.message(UserResponse.comment)
async def write_user_comment(message: Message, state: FSMContext):
    """Сохраняет запись в результирующей таблице со статусом FinalStatus.failed"""
    employee, sent_process = await ActionManager.check_user_response(str(message.from_user.id))

    # Если пользователь действительно 'обработал' сообщение - предлагаем заполнить журнал эксплуатации
    if employee and sent_process:
        await state.update_data({"comment": message.text})
        await message.answer("Хотите добавить запись в журнал эксплуатации ?", reply_markup=yes_or_no_keyboard)
    else:
        await message.answer("Вам не было отправлено сообщений")
        await state.clear()


def register_user_response(dp):
    dp.include_router(user_answer)
