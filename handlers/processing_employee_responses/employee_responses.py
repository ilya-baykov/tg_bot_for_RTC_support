import logging
from datetime import datetime, timedelta
from typing import Tuple, Union

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from middlewares.ThrottlingMiddleware import ThrottlingMiddleware
from database.CRUD.update import ActionsTodayUpdater
from database.CRUD.сreate import employees_reader, actions_today_reader, input_table_reader, employees_updater, \
    ReportCreator
from database.enums import FinalStatus, ActionStatus, EmployeesStatus
from database.models import Employees, ActionsToday
from handlers.processing_employee_responses.state import UserResponse
from run_app.main_objects import scheduler
from sent_task_to_emploeyee.sending_messages import add_task_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

actions_today_updater = ActionsTodayUpdater()
report_creator = ReportCreator()

user_answer = Router()


class ActionManager:
    @staticmethod
    async def check_user_response(user_telegram_id: str) -> Tuple[Union[Employees, None], Union[ActionsToday, None]]:
        """
        Делает проверку пользователя и наличия его задачи со статусом 'Отправлено'

            Если пользователь существует и ему было доставлено сообщение
              :returns возвращает объект сотрудника и объект отправленного процесса
            Если пользователь существует, но ему не было отправлено сообщение
                :returns объект сотрудника
            Ecли такого пользователя не существует:
                :returns None, None

        """
        employee = await employees_reader.get_employee_by_telegram_id_or_username(telegram_id=user_telegram_id)
        if employee:
            sent_process = await actions_today_reader.get_submitted_task_by_employee_id(employee.id)
            return employee, sent_process
        return None, None

    @staticmethod
    async def update_status(employee: Employees, sent_process: ActionsToday):
        """
        Обновляет статусы у сотрудника, получившего сообщение и процесса, который был отправлен и обработан.
        Отправляет действие в планировщик
        """
        await actions_today_updater.update_status(action=sent_process, status=ActionStatus.completed)
        await employees_updater.update_status(employee, EmployeesStatus.available)

        next_sent_processes = await actions_today_reader.get_queued_to_be_added_actions_by_employee_id(employee.id)
        if next_sent_processes:
            next_process = next_sent_processes[0]
            logging.info(f"Следующее действие на отправку: {next_process.id}")

            await actions_today_updater.update_status(next_process, ActionStatus.waiting_to_be_sent)
            await add_task_scheduler(action_task=next_process, scheduler=scheduler)

    @staticmethod
    async def filling_out_report(user_telegram_id: str, status: FinalStatus, comment: str) -> str:
        """Создает новую строку в результирующей таблице"""
        employee, sent_process = await ActionManager.check_user_response(user_telegram_id)
        if employee and sent_process:
            current_time = datetime.now()

            task_from_input_table = await input_table_reader.get_input_task_by_id(sent_process.input_data_id)
            actual_dispatch_time = sent_process.actual_time_message

            time_difference = current_time - actual_dispatch_time
            time_difference_without_microseconds = time_difference - timedelta(
                microseconds=time_difference.microseconds)

            await report_creator.create_new_report(
                action_id=sent_process.id,
                employee_id=employee.id,
                expected_dispatch_time=datetime.combine(datetime.today(), task_from_input_table.scheduled_time),
                actual_dispatch_time=actual_dispatch_time,
                employee_response_time=current_time,
                elapsed_time=time_difference_without_microseconds,
                status=status,
                comment=comment
            )
            await ActionManager.update_status(employee, sent_process)
            return "Отлично, мы записали это в БД"
        elif employee and sent_process is None:
            return "Вам не было отправлено сообщений"
        else:
            return "Для вас нет доступа к этому функционалу. Попробуйте зарегистрироваться с помощью команды start"


@user_answer.message(F.text == "Выполнено")
async def user_response(message: Message, state: FSMContext):
    text_message = await ActionManager.filling_out_report(
        user_telegram_id=str(message.from_user.id),
        status=FinalStatus.successfully,
        comment="Успешно"
    )
    await message.answer(text_message)


@user_answer.message(F.text == "Не выполнено")
async def user_response(message: Message, state: FSMContext):
    await state.set_state(UserResponse.comment)
    await message.answer("Напиши комментарий")


@user_answer.message(UserResponse.comment)
async def write_user_comment(message: Message, state: FSMContext):
    text_message = await ActionManager.filling_out_report(
        user_telegram_id=str(message.from_user.id),
        status=FinalStatus.failed,
        comment=message.text
    )
    await state.set_state(UserResponse.wait_message)
    await message.answer(text_message)


unknown_command = Router()
unknown_command.message.middleware(ThrottlingMiddleware(limit=10))



@unknown_command.message()
async def unknown_response(message: Message):
    await message.answer("Неизвестная команда")


def register_user_response(dp):
    dp.include_router(user_answer)
    dp.include_router(unknown_command)
