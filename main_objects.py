import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.DataBase import DataBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = DataBase()
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")  # Создание планировщика задач


async def start_scheduler(scheduler):
    scheduler.start()
    logger.info(f"Планировщик заданий {scheduler} запущен ")
