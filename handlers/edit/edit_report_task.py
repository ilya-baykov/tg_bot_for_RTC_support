from datetime import datetime, timedelta
import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from apscheduler.jobstores.base import JobLookupError
from apscheduler.triggers.date import DateTrigger

from database.CRUD.read import ActionsTodayReader, EmployeesReader, ReportReader, SchedulerTasksReader
from database.CRUD.update import ReportUpdater, SchedulerTasksUpdater
from database.enums import FinalStatus, SchedulerStatus
from handlers.edit.keyboard import inline_today, TaskInfo
from handlers.filters_general import RegisteredUser
from run_app.main_objects import scheduler
from sent_task_to_emploeyee.keyboard import keyboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

edit_router = Router()


class EditState(StatesGroup):
    on_edit = State()
    write_comment = State()


@edit_router.message(RegisteredUser(), Command('edit'))
async def edit_task(message: Message, state: FSMContext):
    employee = await EmployeesReader().get_employee_by_telegram_id_or_username(telegram_id=str(message.from_user.id))

    last_tasks = await ActionsTodayReader().get_completed_actions_by_employee_id(employee.id)

    message_text = 'Выбери процесс,который хочешь редактировать' if last_tasks else "Сегодня вы еще не обработали ни одного действия"

    await message.reply(text=message_text, reply_markup=await inline_today(last_tasks))


@edit_router.callback_query(TaskInfo.filter())
async def process_task_selection(callback_query: CallbackQuery, callback_data: TaskInfo, state: FSMContext):
    employee = await EmployeesReader.get_employee_by_telegram_id_or_username(
        telegram_id=str(callback_query.from_user.id))  # Получаем сотрудника

    # ДеЙствие планировщика поставить на паузу
    task_in_scheduler = await SchedulerTasksReader().get_last_task_by_employee(employee_id=employee.id)
    if task_in_scheduler:
        # Остановка задачи из планировщика по ID
        try:
            scheduler.pause_job(task_in_scheduler.id)
            # Изменяем статус задачи в планировщике
            await SchedulerTasksUpdater.update_params(task=task_in_scheduler, status=SchedulerStatus.suspended)
            logger.info(f"Задача с ID {task_in_scheduler.id} остановлена.")
        except JobLookupError:
            logger.error(f"Задача с ID {task_in_scheduler.id} не найдена в планировщике.")
        except Exception as e:
            print(e)
        # Сохраняем номер задач для редактирования
        await state.update_data(scheduler_task_id=task_in_scheduler.id)

    await callback_query.answer()
    await state.update_data(task_id=callback_data.task_id)
    await state.set_state(EditState.on_edit)

    await callback_query.message.answer(
        text=f"Отредактируйте задачу {callback_data.task_id}",
        reply_markup=keyboard
    )


@edit_router.message(EditState.on_edit, F.text.in_({"Выполнено", "Не выполнено"}))
async def test(message: Message, state: FSMContext):
    await state.set_state(EditState.write_comment)
    if message.text == "Выполнено":
        await state.update_data({"status": FinalStatus.successfully})
    elif message.text == "Не выполнено":
        await state.update_data({"status": FinalStatus.failed})
    await message.answer("Напиши комментарий")


@edit_router.message(EditState.write_comment)
async def test_2(message: Message, state: FSMContext):
    current_time = datetime.now()
    user_data = await state.get_data()
    task_id = user_data.get("task_id")
    task_in_scheduler_id = user_data.get('scheduler_task_id')
    if task_in_scheduler_id:
        task_in_scheduler = await SchedulerTasksReader.get_tasks(task_in_scheduler_id)

        # Если следующая задача должна была выполниться - переводим время
        if task_in_scheduler.expected_completion_time > current_time + timedelta(seconds=10):
            time = task_in_scheduler.expected_completion_time
        else:
            time = current_time + timedelta(seconds=10)

        await SchedulerTasksUpdater.update_params(task=task_in_scheduler,
                                                  status=SchedulerStatus.awaiting_dispatch,
                                                  time=time)

        new_trigger = DateTrigger(run_date=time)

        # Изменение времени задачи
        scheduler.modify_job(task_in_scheduler_id, trigger=new_trigger)
        # Возобновление задачи
        scheduler.resume_job(task_in_scheduler_id)

        logger.info(f"Время выполнения задачи с ID {task_in_scheduler_id} установлено на :{time}.")

    status = user_data.get("status")
    report = await ReportReader().get_report_by_actions_id(int(task_id))
    await ReportUpdater().update_params(report, status=status, comment=message.text)
    await state.clear()
    await message.answer("Изменеия успешно сохранились в таблицу.")


def register_edit_handlers(dp):
    dp.include_router(edit_router)
