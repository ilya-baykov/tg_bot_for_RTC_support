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


async def check_user_response(user_telegram_id: str):
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
        employee_id = employee.id
        sent_process = await actions_reader.get_submitted_task_by_employee_id(employee_id)  # Текущая задача
        if sent_process:
            return employee, sent_process
        else:
            return employee, None
    return None, None


async def update_status(employee, sent_process):
    """
    Обновляет статусы у сотрудника, получившего сообщение и процесса, который был отправлен и обработан.
    Отправляет действие в планировщик
    """

    await actions_updater.update_status(action=sent_process, status=ActionStatus.completed)  # Действие завершено
    await employees_updater.update_status(employee, EmployeesStatus.available)  # Сотрудник готов к новым сообщениям

    # Получение следующих действий из очереди
    next_sent_processes = await actions_reader.get_queued_to_be_added_actions_by_employee_id(employee.id)

    if next_sent_processes:
        next_process = next_sent_processes[0]  # Первое в очереди действие на добавление в планировщик
        logging.info(f"Следующее действие на отправку: {next_process.id}")

        await actions_updater.update_status(next_process, ActionStatus.waiting_to_be_sent)  # Смена статуса действия
        await add_task_scheduler(action_task=next_process, scheduler=scheduler)  # Добавление задачи в планировщик


async def filling_out_report(user_telegram_id: str, status: FinalStatus, comment: str) -> str:
    """Создает новую строку в результирующей таблице"""
    employee, sent_process = await check_user_response(user_telegram_id)
    if employee and sent_process:
        current_time = datetime.datetime.now()  # Текущее время

        # Получаем действие из исходной таблицы (для получения ожидаемого времени)
        task_from_intput_table = await input_table_reader.get_input_task_by_id(sent_process.input_data_id)

        actual_dispatch_time = sent_process.actual_time_message

        # Разница во времени
        time_difference = current_time - actual_dispatch_time
        # Убираем миллисекунды

        time_difference_without_microseconds = time_difference - datetime.timedelta(
            microseconds=time_difference.microseconds)

        await report_creator.create_new_report(action_id=sent_process.id, employee_id=employee.id,
                                               expected_dispatch_time=task_from_intput_table.scheduled_time,
                                               actual_dispatch_time=actual_dispatch_time,
                                               employee_response_time=current_time,
                                               elapsed_time=time_difference_without_microseconds,
                                               status=status, comment=comment)
        await update_status(employee, sent_process)
        return "Отлично, мы записали это в БД"
    elif employee and sent_process is None:
        return "Вам не было отправлено сообщений"
    else:
        return "Для вас нет доступа к этому функционалу. Попробуйте зарегистрироваться с помощью команды start"


@user_answer.message(F.text == "Выполнено")
async def user_response(message: Message, state: FSMContext):
    text_message = await filling_out_report(user_telegram_id=str(message.from_user.id), status=FinalStatus.successfully,
                                            comment="Успешно")
    await message.answer(text_message)


@user_answer.message(F.text == "Не выполнено")
async def user_response(message: Message, state: FSMContext):
    await state.set_state(UserResponse.comment)
    await message.answer("Напиши комментарий")


@user_answer.message(UserResponse.comment)
async def write_user_comment(message: Message, state: FSMContext):
    text_message = await filling_out_report(user_telegram_id=str(message.from_user.id), status=FinalStatus.failed,
                                            comment=message.text)
    await state.set_state(UserResponse.wait_message)
    await message.answer(text_message)


@user_answer.message()
async def unknown_response(message: Message):
    await message.answer("Неизвестная команда")


def register_user_response(dp):
    dp.include_router(user_answer)
