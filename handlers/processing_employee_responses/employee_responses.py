import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import datetime

from database.CRUD.update import ActionsUpdater
from database.CRUD.сreate import employees_reader, actions_reader, input_table_reader, employees_updater, ReportCreator
from database.enums import FinalStatus, ActionStatus, EmployeesStatus
from handlers.processing_employee_responses.state import UserResponse
from run_app.main_objects import scheduler
from sent_task_to_emploeyee.sending_messages import add_task_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

actions_updater = ActionsUpdater()
report_creator = ReportCreator()

user_answer = Router()


@user_answer.message(F.text == "Выполнено")
async def user_response(message: Message, state: FSMContext):
    employee = await employees_reader.get_employee_by_telegram_id_or_username(telegram_id=str(message.from_user.id))
    if employee:
        employee_id = employee.id
        sent_process = await actions_reader.get_submitted_task_by_employee_id(employee_id)  # Текущая задача
        if sent_process:
            task_from_intput_table = await input_table_reader.get_input_task_by_id(sent_process.input_data_id)
            actual_dispatch_time = sent_process.actual_time_message
            await report_creator.create_new_report(action_id=sent_process.id,
                                                   employee_id=employee_id,
                                                   expected_dispatch_time=task_from_intput_table.scheduled_time,
                                                   actual_dispatch_time=actual_dispatch_time,
                                                   employee_response_time=datetime.datetime.now(),
                                                   elapsed_time=datetime.datetime.now() - actual_dispatch_time,
                                                   status=FinalStatus.successfully,
                                                   comment="Успешно"),
            await actions_updater.update_status(action=sent_process, status=ActionStatus.completed)
            await employees_updater.update_status(employee, EmployeesStatus.available)

            next_sent_processes = await actions_reader.get_queued_to_be_added_actions_by_employee_id(employee_id)

            if next_sent_processes:
                next_process = next_sent_processes[0]
                logging.info(f"Следующее действие на отправку: {next_process.id}")

                await actions_updater.update_status(next_process, ActionStatus.waiting_to_be_sent)
                await add_task_scheduler(action_task=next_process, scheduler=scheduler)

            await message.answer(f"Отлично, мы записали это в БД")
        else:
            await message.answer("Вам не было отправлено сообщений")

    else:
        await message.answer(
            "Для вас нет доступа к этому функционалу. Попробуйте зарегистрироваться с помощью команды start")


@user_answer.message(UserResponse.wait_message, F.text == "Не выполнено")
async def user_response(message: Message, state: FSMContext):
    await state.set_state(UserResponse.comment)
    await message.answer("Напиши комментарий")


@user_answer.message(UserResponse.comment)
async def write_user_comment(message: Message, state: FSMContext):
    await message.answer("Спасибо за уточнение, мы записали это в БД")
    await state.set_state(UserResponse.wait_message)


def register_user_response(dp):
    dp.include_router(user_answer)
