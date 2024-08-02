import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from database.CRUD.read import EmployeesReader, ReportReader, SchedulerTasksReader
from database.CRUD.update import ReportUpdater
from database.enums import FinalStatus
from handlers.edit.keyboard import inline_today, TaskInfo
from handlers.edit.state import EditState
from handlers.filters_general import RegisteredUser
from run_app.main_objects import scheduler
from sent_task_to_emploeyee.keyboard import keyboard
from utility.sheduler_functions import resume_scheduler_task, pause_scheduler_task

logger = logging.getLogger(__name__)

edit_router = Router()


@edit_router.message(RegisteredUser(), Command('edit'))
async def edit_task(message: Message, state: FSMContext):
    employee = await EmployeesReader().get_employee_by_telegram_id_or_username(telegram_id=str(message.from_user.id))

    last_tasks = await ReportReader().get_report_by_employee_name(employee.name)

    message_text = 'Выбери процесс,который хочешь редактировать' if last_tasks else "Сегодня вы еще не обработали ни одного действия"

    await message.reply(text=message_text, reply_markup=await inline_today(last_tasks))


@edit_router.callback_query(TaskInfo.filter())
async def process_task_selection(callback_query: CallbackQuery, callback_data: TaskInfo, state: FSMContext):
    employee = await EmployeesReader.get_employee_by_telegram_id_or_username(
        telegram_id=str(callback_query.from_user.id))  # Получаем сотрудника

    # Действие планировщика поставить на паузу
    task_in_scheduler = await SchedulerTasksReader().get_last_task_by_employee(employee_id=employee.id)
    await pause_scheduler_task(task_in_scheduler)
    await state.update_data(scheduler_task_id=task_in_scheduler.id)

    await callback_query.answer()
    await state.update_data(task_id=callback_data.task_id)
    await state.set_state(EditState.on_edit)

    await callback_query.message.answer(
        text=f"Отредактируйте задачу {callback_data.task_id}",
        reply_markup=keyboard
    )


@edit_router.message(EditState.on_edit, F.text.in_({"Выполнено", "Не выполнено"}))
async def state_update_data(message: Message, state: FSMContext):
    await state.set_state(EditState.write_comment)
    if message.text == "Выполнено":
        await state.update_data({"status": FinalStatus.successfully})
    elif message.text == "Не выполнено":
        await state.update_data({"status": FinalStatus.failed})
    await message.answer("Напиши комментарий")


@edit_router.message(EditState.write_comment)
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


def register_edit_handlers(dp):
    dp.include_router(edit_router)
