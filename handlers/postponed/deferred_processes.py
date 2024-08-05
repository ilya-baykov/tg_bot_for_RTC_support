import logging
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database.CRUD.read import EmployeesReader, SchedulerTasksReader, ActionsTodayReader, ClearInputTableReader
from database.CRUD.сreate import employees_updater
from database.enums import FinalStatus, ActionStatus, EmployeesStatus
from database.models import Employees
from handlers.filters_general import RegisteredUser
from handlers.postponed.keyboard import inline_deferred_tasks, ActionInfo, keyboard_for_report
from handlers.postponed.state import PostponedState
from utility.ActionManager import report_creator, actions_today_updater
from utility.sheduler_functions import pause_scheduler_task, resume_scheduler_task

logger = logging.getLogger(__name__)

postponed_router = Router()


@postponed_router.message(RegisteredUser(), Command('deferred_tasks'))
async def choice_deferred_tasks(message: Message, state: FSMContext):
    """Предоставляет клавиатуру для выбора одной из задач со статусом FinalStatus.postponed"""
    employee = await EmployeesReader().get_employee_by_telegram_id_or_username(telegram_id=str(message.from_user.id))
    await state.update_data(employee=employee)
    deferred_tasks = await ActionsTodayReader.get_deferred_actions(employee.id)
    message_text = "Выбери отложенный процесс,который хочешь обработать" if deferred_tasks else "У вас нет отложенных задач"

    await message.reply(text=message_text, reply_markup=await (inline_deferred_tasks(deferred_tasks)))


@postponed_router.callback_query(ActionInfo.filter())
async def take_selection_deferred_tasks(callback_query: CallbackQuery, callback_data: ActionInfo, state: FSMContext):
    """Обрабатывает выбор отложенного процесса"""
    employee = await EmployeesReader.get_employee_by_telegram_id_or_username(
        telegram_id=str(callback_query.from_user.id))  # Получаем сотрудника

    # Действие планировщика поставить на паузу
    task_in_scheduler = await SchedulerTasksReader().get_last_task_by_employee(employee_id=employee.id)
    if task_in_scheduler:
        await pause_scheduler_task(task_in_scheduler)
        await state.update_data(scheduler_task_id=task_in_scheduler.id)

    await callback_query.answer()
    await state.update_data(action_task_id=callback_data.action_task_id)
    await state.set_state(PostponedState.getting_task)

    await callback_query.message.answer(
        text=f"Обработайте отложенную задачу ",
        reply_markup=keyboard_for_report)


@postponed_router.message(PostponedState.getting_task, F.text == "Выполнено")
async def deferred_process_successful(message: Message, state: FSMContext):
    """Заполняет запись в отчётной таблице со статусом 'ActionStatus.completed' """
    user_data = await state.get_data()

    message_response = await report_save(employee=user_data.get("employee"), task_id=user_data.get("action_task_id"),
                                         status=FinalStatus.successfully, comment=message.text)

    task_in_scheduler_id = user_data.get('scheduler_task_id')
    if task_in_scheduler_id: await resume_scheduler_task(task_in_scheduler_id)
    await state.clear()
    await message.answer(message_response)


@postponed_router.message(PostponedState.getting_task, F.text == "Не выполнено")
async def deferred_process_failed(message: Message, state: FSMContext):
    """Переходим в следующее состояние - ввода комментария при отклоненном процессе"""
    await message.answer("Напишите комментарий")
    await state.set_state(PostponedState.task_comment)


@postponed_router.message(PostponedState.task_comment)
async def change_entry_report(message: Message, state: FSMContext):
    """Получаем комментарий по отложенному отклоненному процессу и записываем его в отчётную таблицу"""
    user_data = await state.get_data()

    message_response = await report_save(employee=user_data.get("employee"), task_id=user_data.get("action_task_id"),
                                         status=FinalStatus.failed, comment=message.text)
    task_in_scheduler_id = user_data.get('scheduler_task_id')
    if task_in_scheduler_id: await resume_scheduler_task(task_in_scheduler_id)
    await state.clear()
    await message.answer(message_response)


async def report_save(employee: Employees, task_id: int, status: FinalStatus, comment: str) -> str:
    """Сохраняет запись в отчётной таблице для отложенного процесса.
       Возвращает сообщение пользователю об успешности записи
    """
    try:
        task = await ActionsTodayReader.get_action_by_id(task_id)
        process = await ClearInputTableReader.get_input_task_by_id(task.input_data_id)

        actual_dispatch_time = task.actual_time_message

        time_difference = datetime.now() - actual_dispatch_time
        time_difference_without_microseconds = time_difference - timedelta(microseconds=time_difference.microseconds)

        await report_creator.create_new_report(
            process_name=process.process_name,
            action_description=process.action_description,
            employee_name=employee.name,
            expected_dispatch_time=datetime.combine(datetime.today(), process.scheduled_time),
            actual_dispatch_time=actual_dispatch_time,
            employee_response_time=datetime.now(),
            elapsed_time=time_difference_without_microseconds,
            status=status,
            comment=comment)
        await actions_today_updater.update_status(action=task, status=ActionStatus.completed)
        await employees_updater.update_status(employee, EmployeesStatus.available)
        return "Отлично, запись добавлена в БД"
    except Exception as e:
        logger.error(
            f"Ошибка при попытке внести запись в отчёт по отложенной задаче {task_id} : {e} ")
        return "При попытке сохранить запись в отчёт произошла неизвестная ошибка"


def register_postponed_handlers(dp):
    dp.include_router(postponed_router)
