import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database.CRUD.read import EmployeesReader, SchedulerTasksReader, ActionsTodayReader, ReportReader
from database.CRUD.update import ReportUpdater
from database.enums import FinalStatus
from handlers.filters_general import RegisteredUser
from handlers.postponed.keyboard import inline_deferred_tasks, ActionInfo, keyboard_for_report
from handlers.postponed.state import PostponedState
from run_app.main_objects import scheduler
from utility.sheduler_functions import pause_scheduler_task, resume_scheduler_task

logger = logging.getLogger(__name__)

postponed_router = Router()


@postponed_router.message(RegisteredUser(), Command('deferred_tasks'))
async def choice_deferred_tasks(message: Message, state: FSMContext):
    """Предоставляет клавиатуру для выбора одной из задач со статусом FinalStatus.postponed"""
    employee = await EmployeesReader().get_employee_by_telegram_id_or_username(telegram_id=str(message.from_user.id))
    deferred_tasks = await ActionsTodayReader.get_deferred_actions(employee.id)
    message_text = "Выбери отложенный процесс,который хочешь обработать" if deferred_tasks else "У вас нет отложенных задач"

    await message.reply(text=message_text, reply_markup=await (inline_deferred_tasks(deferred_tasks)))


@postponed_router.callback_query(ActionInfo.filter())
async def take_selection_deferred_tasks(callback_query: CallbackQuery, callback_data: ActionInfo, state: FSMContext):
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


@postponed_router.message(PostponedState.getting_task, F.text.in_({"Выполнено", "Не выполнено"}))
async def state_update_data(message: Message, state: FSMContext):
    await state.set_state(PostponedState.task_processing)
    if message.text == "Выполнено":
        await state.update_data({"status": FinalStatus.successfully})
    elif message.text == "Не выполнено":
        await state.update_data({"status": FinalStatus.failed})
    await message.answer("Напиши комментарий")


@postponed_router.message(PostponedState.task_processing)
async def change_entry_report(message: Message, state: FSMContext):
    user_data = await state.get_data()
    task_id = user_data.get("task_id")
    task_in_scheduler_id = user_data.get('scheduler_task_id')
    if task_in_scheduler_id:
        await resume_scheduler_task(task_in_scheduler_id)
    status = user_data.get("status")
    report = await ReportReader().get_report_by_id(int(task_id))
    await ReportUpdater().update_params(report, status=status, comment=message.text)
    await state.clear()
    await message.answer("Изменеия успешно сохранились в таблицу.")


def register_postponed_handlers(dp):
    dp.include_router(postponed_router)
