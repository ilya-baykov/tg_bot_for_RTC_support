from sqlalchemy import select, asc
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.config import settings
from database.models import *

import logging

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
            request.add(Employee(
                telegram_username=telegram_username,
                telegram_id=telegram_id,
                name=fullname
            ))
            await request.commit()

    async def add_processes(self, process_name, action_description, employee_id, scheduled_time):
        async with self.Session() as request:
            request.add(Process(
                process_name=process_name,
                action_description=action_description,
                employee_id=employee_id,
                scheduled_time=scheduled_time
            ))

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

            for task in tasks:
                print(f"Task ID: {task.entry_id}, Process Name: {task.process_name}, "
                      f"Scheduled Time: {task.scheduled_time}, Employee Telegram: {task.employee_telegram}, "
                      f"Action_description: {task.action_description}")
