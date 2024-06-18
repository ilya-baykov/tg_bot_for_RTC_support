import logging
from abc import ABC
from typing import List

from sqlalchemy import select, asc
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import joinedload

from database.config import settings
from database.models import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataBase:
    def __init__(self):
        self.db_host = settings.DB_HOST
        self.db_user = settings.DB_USER
        self.db_password = settings.DB_PASS
        self.db_name = settings.DB_NAME
        self.db_connect = settings.DATABASE_URL

        self.async_engine = create_async_engine(self.db_connect)
        self.Session = async_sessionmaker(bind=self.async_engine, class_=AsyncSession)

    async def create_db(self):
        logger.info("Создаются таблицы")

        async with self.async_engine.begin() as connect:
            await connect.run_sync(Base.metadata.create_all)
        logger.info("Таблицы созданы")


class Databases(ABC):
    def __init__(self, db: DataBase):
        self.db = db


class InputDB(Databases):
    async def get_tasks(self):
        logger.info("Получение будущих задач")
        async with self.db.Session() as request:
            query = (
                select(TaskEntry)
                .filter(TaskEntry.scheduled_time > datetime.datetime.now())
                .order_by(asc(TaskEntry.scheduled_time))
            )
            result = await request.execute(query)
            tasks = result.scalars().all()
            return tasks


class EmployeesDB(Databases):

    async def create_new_employer(self, telegram_username: str, telegram_id: int, fullname: str) -> None:
        """
        Метод для создания / регистрации сотрудников в Таблице employees
        :param telegram_username:  никнейм в профиле телеграмма сотрудника
        :param telegram_id: телеграмм-Идентификатор сотрудника
        :param fullname: Имя, которое указано сотрудником в телеграмм-аккаунте ( может отсутствовать )
        :return: Ничего не возвращает.
        """
        async with self.db.Session() as request:
            # Получаем сотрудника ( по его id ).
            existing_employee = await self.get_employee_by_telegram_id(telegram_id=str(telegram_id))

            # Проверяем наличие данного сотрудника в таблице employees
            if existing_employee:
                # Обновляем username, если он изменился
                if existing_employee.telegram_username != telegram_username:
                    existing_employee.telegram_username = telegram_username
                    await request.commit()
                    logger.info(f"Telegram username для telegram_id '{telegram_id}' обновлен на '{telegram_username}'.")
                else:
                    logger.info(f"Пользователь с telegram_id '{telegram_id}' уже существует и не требует обновления.")
            else:
                # Если пользователь не существует, добавляем его
                request.add(Employee(
                    telegram_username=telegram_username,
                    telegram_id=telegram_id,
                    name=fullname
                ))
                await request.commit()

    async def get_employee_by_telegram_username(self, telegram_username):
        async with self.db.Session() as request:
            query = select(Employee).filter_by(telegram_username=telegram_username)
            result = await request.execute(query)
            return result.scalar_one_or_none()

    async def get_employee_by_telegram_id(self, telegram_id):
        async with self.db.Session() as request:
            query = select(Employee).filter_by(telegram_id=str(telegram_id) )
            result = await request.execute(query)
            return result.scalar_one_or_none()


class ProcessDB(Databases):
    async def create_new_proces(self, process_name, action_description, employee_id, scheduled_time):
        async with self.db.Session() as request:
            existing_process = await self.get_proces(process_name, action_description, employee_id, scheduled_time)

            if existing_process:
                logger.info(f"Процесс '{process_name}' уже существует и не будет добавлен.")
            else:
                # Если процесс не существует, добавляем его
                request.add(Process(
                    process_name=process_name,
                    action_description=action_description,
                    employee_id=employee_id,
                    scheduled_time=scheduled_time
                ))
                await request.commit()

    async def create_new_processes(self, tasks: List, db: DataBase = DataBase()):
        logger.info("Создание новых процессов")
        employees = EmployeesDB(db)
        for task in tasks:
            print(f"Task ID: {task.entry_id}, Process Name: {task.process_name}, "
                  f"Scheduled Time: {task.scheduled_time}, Employee Telegram: {task.employee_telegram}, "
                  f"Action_description: {task.action_description}")

            # Получить сотрудника, ответственного за задачу
            employee = await employees.get_employee_by_telegram_username(task.employee_telegram)
            if employee:
                await self.create_new_proces(
                    process_name=task.process_name,
                    action_description=task.action_description,
                    employee_id=employee.employee_id,
                    scheduled_time=task.scheduled_time
                )
            else:
                logger.warning(f"Сотрудник с telegram_username '{task.employee_telegram}' не найден.")

    async def get_proces(self, process_name, action_description, employee_id, scheduled_time):
        async with self.db.Session() as request:
            # Проверяем, существует ли уже процесс с такими же данными
            existing_process_query = select(Process).filter_by(
                process_name=process_name,
                action_description=action_description,
                employee_id=employee_id,
                scheduled_time=scheduled_time
            )
            existing_process_result = await request.execute(existing_process_query)
            existing_process = existing_process_result.scalar_one_or_none()
            return existing_process

    async def get_process_by_name(self, process_name):
        async with self.db.Session() as request:
            query = select(Process).filter_by(process_name=process_name)
            result = await request.execute(query)
            return result.scalar_one_or_none()

    async def get_all_processes(self):
        async with self.db.Session() as request:
            query = select(Process).options(joinedload(Process.employee)).order_by(asc(Process.scheduled_time))
            result = await request.execute(query)
            processes = result.scalars().all()
            return processes


class NotificationDB(Databases):
    pass


class EmployeePhonesDB(Databases):

    async def get_employee_by_phone(self, phone_number):
        async with self.db.Session() as request:
            query = select(EmployeePhones).filter_by(phone_number=phone_number)
            result = await request.execute(query)
            return result.scalar_one_or_none()
