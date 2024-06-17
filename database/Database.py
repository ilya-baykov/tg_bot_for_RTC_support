import logging

from sqlalchemy import select, asc
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import joinedload

from database.config import settings
from database.models import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
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

    async def add_employees(self, telegram_username, telegram_id, fullname):
        async with self.Session() as request:
            # Проверяем, существует ли пользователь с данным telegram_id
            existing_employee_query = select(Employee).filter_by(telegram_id=str(telegram_id))
            existing_employee_result = await request.execute(existing_employee_query)
            existing_employee = existing_employee_result.scalar_one_or_none()

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

    async def add_processes(self, process_name, action_description, employee_id, scheduled_time):
        async with self.Session() as request:
            # Проверяем, существует ли уже процесс с такими же данными
            existing_process_query = select(Process).filter_by(
                process_name=process_name,
                action_description=action_description,
                employee_id=employee_id,
                scheduled_time=scheduled_time
            )
            existing_process_result = await request.execute(existing_process_query)
            existing_process = existing_process_result.scalar_one_or_none()

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

    async def create_processes(self, tasks):
        logger.info("Создание новых процессов")
        async with self.Session() as request:
            for task in tasks:
                print(f"Task ID: {task.entry_id}, Process Name: {task.process_name}, "
                      f"Scheduled Time: {task.scheduled_time}, Employee Telegram: {task.employee_telegram}, "
                      f"Action_description: {task.action_description}")

                # Получить employee_id по telegram_username
                employee_query = select(Employee.employee_id).filter_by(telegram_username=task.employee_telegram)
                employee_result = await request.execute(employee_query)
                employee_id = employee_result.scalar_one_or_none()

                if employee_id:
                    await self.add_processes(
                        process_name=task.process_name,
                        action_description=task.action_description,
                        employee_id=employee_id,
                        scheduled_time=task.scheduled_time
                    )
                else:
                    logger.warning(f"Сотрудник с telegram_username '{task.employee_telegram}' не найден.")

    async def select_future_tasks(self):
        logger.info("Получение будущих задач")
        async with self.Session() as request:
            query = (
                select(TaskEntry)
                .filter(TaskEntry.scheduled_time > datetime.datetime.now())
                .order_by(asc(TaskEntry.scheduled_time))
            )
            result = await request.execute(query)
            tasks = result.scalars().all()
            return tasks

    async def get_employee_by_telegram_username(self, telegram_username):
        async with self.Session() as request:
            query = select(Employee).filter_by(telegram_username=telegram_username)
            result = await request.execute(query)
            return result.scalar_one_or_none()

    async def get_process_by_name(self, process_name):
        async with self.Session() as request:
            query = select(Process).filter_by(process_name=process_name)
            result = await request.execute(query)
            return result.scalar_one_or_none()

    async def get_all_processes(self):
        async with self.Session() as request:
            query = select(Process).options(joinedload(Process.employee)).order_by(asc(Process.scheduled_time))
            result = await request.execute(query)
            processes = result.scalars().all()
            return processes
