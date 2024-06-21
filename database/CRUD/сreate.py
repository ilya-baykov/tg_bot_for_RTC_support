import logging

from main_objects import db
from database.models import *
from database.CRUD.read import EmployeesReader, InputTableReader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

employees_reader = EmployeesReader()
input_table_reader = InputTableReader()


class EmployeesCreator:
    @staticmethod
    async def create_new_employees(name: str | None, telegram_username: str, telegram_id: str | int):
        """Добавляем / Регистрируем нового сотрудника или изменяем username у текущего сотрудника """
        async with db.Session() as request:
            employee = await employees_reader.get_employee_by_telegram_id_or_username(telegram_id=str(telegram_id))
            if employee:
                # Если сотрудник изменил username - заменяем значение в таблице
                if employee.telegram_username != telegram_username:
                    employee.telegram_username = telegram_username
                    await request.commit()
                    logger.info(f"Telegram username для telegram_id '{telegram_id}' обновлен на '{telegram_username}'.")
                else:
                    logger.info(f"Пользователь с telegram_id '{telegram_id}' уже существует и не требует обновления.")
            else:
                # Создать нового сотрудника
                request.add(Employees(
                    name=name,
                    telegram_username=telegram_username,
                    telegram_id=telegram_id,
                ))
                logger.info(f"Пользователь с telegram_id '{telegram_id}' добавлен в таблицу employees.")

                await request.commit()


class ActionsCreator:
    @staticmethod
    async def create_new_action():
        """Формируем актуальные задачи из исходной таблицы """
        async with db.Session() as request:
            tasks = await input_table_reader.get_all_actions()
            employee_tasks_cache = {}
            for task in tasks:
                # Получаем сотрудника
                employee = await employees_reader.get_employee_by_telegram_id_or_username(task.telegram_username)
                if employee:

                    # Получаем количество задач у сотрудника и кешируем эти данные
                    if employee.id not in employee_tasks_cache:
                        employee_tasks = await EmployeesReader.get_all_employee_tasks(employee_id=employee.id)
                        employee_tasks_cache[employee.id] = len(employee_tasks)

                    print(f"ID сотрудника : {employee.id}, Количество его задач: {employee_tasks_cache[employee.id]}")

                    quantity_employee_tasks = employee_tasks_cache[employee.id]

                    # Формируем статус задачи. (Готов к отправке или ожидает добавления в список задач)
                    status = ActionStatus.waiting_to_be_sent if quantity_employee_tasks == 0 else ActionStatus.queued_to_be_added

                    # Создаем новый процесс
                    request.add(Actions(
                        input_data_id=task.id,
                        employee_id=employee.id,
                        status=status
                    ))
                    employee_tasks_cache[employee.id] += 1
                    await request.commit()
                    logger.info(f"Задача {task.process_name} была добавлена со статусом {status}")

                else:
                    logger.warning(f"Сотрудник с telegram_username '{task.employee_telegram}' не найден.")
