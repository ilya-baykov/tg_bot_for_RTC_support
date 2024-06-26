import logging

from os import environ

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.DataBase import DataBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = DataBase()
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")  # Создание планировщика задач
bot = Bot(token=environ.get('TOKEN', 'define me!'))


async def start_scheduler(scheduler):
    if scheduler.running:
        scheduler.shutdown(wait=False)  # Закрываем прошлый планировщик задач
        logger.info("Прошлые задачи планировщика были очищены")

    scheduler.start()
    logger.info(f"Планировщик заданий {scheduler} запущен")
    logger.info("Все предыдущие задачи планировщика были удалены")



