import logging

from database.CRUD.update import EmployeesUpdater
from main_objects import db
from database.models import *
from database.CRUD.read import EmployeesReader, InputTableReader, ActionsReader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

employees_reader = EmployeesReader()
input_table_reader = InputTableReader()
employees_updater = EmployeesUpdater()
actions_reader = ActionsReader()


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
            tasks = await input_table_reader.get_all_actions()  # Получаем список всех задач из входной таблицы
            busy_employee = {}  # Словарь 'занятых' сотрудниклв
            for task in tasks:

                # Проверка нахождения задачи в таблице actions (по ключу из входной таблицы)
                availability_check = await actions_reader.get_action(task.id)
                if availability_check:
                    logger.info(f"Задача {task.id} уже была создана.")
                else:

                    # Если пользователь в словаре занятых сотрудников, то делаем задачу со статусом "ожидает добавления"
                    if task.telegram_username in busy_employee:
                        status = ActionStatus.queued_to_be_added

                    # Иначе - добавляем пользователя в список занятых сотрудников
                    else:
                        # Получаем сотрудника из БД
                        employee = await employees_reader.get_employee_by_telegram_id_or_username(
                            task.telegram_username)
                        if employee:
                            # Добавляем сотрудника в словарь занятых
                            busy_employee[task.telegram_username] = employee

                            # Получаем количество задач у сотрудника
                            employee_quantity_tasks = await employees_reader.get_all_employee_tasks(
                                employee_id=employee.id)

                            # Устанавливаем соответствующий статус процессу исходя из количества действий у сотрудника
                            if len(employee_quantity_tasks) > 0:
                                status = ActionStatus.queued_to_be_added
                            else:
                                status = ActionStatus.waiting_to_be_sent
                        else:
                            logger.warning(f"Сотрудник с telegram_username '{task.employee_telegram}' не найден.")
                            continue

                    # Создаем новый процесс
                    request.add(Actions(
                        input_data_id=task.id,
                        employee_id=employee.id,
                        status=status
                    ))

                    await request.commit()
                    logger.info(f"Задача {task.process_name} была добавлена со статусом {status}")
