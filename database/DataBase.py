from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.config import settings
from database.models import *

import logging

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

    async def reset_database(self):
        logger.info("Очищаются все таблицы")

        async with self.async_engine.begin() as connect:
            await connect.run_sync(Base.metadata.drop_all)
        logger.info("БД очищена")
