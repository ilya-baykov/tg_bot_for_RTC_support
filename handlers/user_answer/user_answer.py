import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from handlers.send_task_notifications.adding_messages_queue import getting_employees_current_task
from handlers.user_answer.state import UserResponse
from database_old.Database import NotificationDB, EmployeesDB, ProcessDB, DataBase, NotificationProcessStatus, \
    ProcessStatus, EmployeeStatus

user_answer = Router()
db = DataBase()
employeesDB = EmployeesDB(db)
processDB = ProcessDB(db)
notificationDB = NotificationDB(db)


@user_answer.message(UserResponse.wait_message, F.text == "Выполнено")
async def user_response(message: Message, state: FSMContext):
    employee = await employeesDB.get_employee_by_telegram_id(telegram_id=message.from_user.id)
    if employee:
        employee_id = employee.employee_id
        sent_processes = await processDB.get_all_sent_processes_by_employee_id(employee_id)
        print(len(sent_processes))
        if sent_processes:
            sent_process = sent_processes[0]  # Последний отправленный запрос
            await notificationDB.create_new_notification(process_id=sent_process.process_id,
                                                         employee_id=employee_id,
                                                         sent_time=sent_process.scheduled_time,
                                                         response_time=datetime.datetime.now(),
                                                         response_status=NotificationProcessStatus.ok,
                                                         comment="Успешно")  # Фиксируем ответ в таблицу
            await processDB.change_status(process=sent_process, status=ProcessStatus.completed)
            await employeesDB.change_status(employee=employee, status=EmployeeStatus.available)

            next_sent_process = await processDB.get_all_queued_to_be_added_by_employee_id(
                employee.employee_id)

            if next_sent_process:
                first_process = next_sent_process[0]
                print(f"Есть следующее задание на добавление: {first_process.process_name}")

                await processDB.change_status(first_process, ProcessStatus.waiting_to_be_sent)
                await getting_employees_current_task()

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
