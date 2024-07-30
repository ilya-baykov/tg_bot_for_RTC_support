import logging
import json
from os import environ

import aiofiles
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.DataBase import DataBase

logger = logging.getLogger(__name__)

db = DataBase()
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")  # Создание планировщика задач

# session = AiohttpSession(proxy='http://pxs.rt.ru:3128')
# bot = Bot(token=environ.get('TOKEN', 'define me!'), session=session)


bot = Bot(token=environ.get('TOKEN', 'define me!'))


async def start_scheduler(scheduler):
    if scheduler.running:
        scheduler.shutdown(wait=False)  # Закрываем прошлый планировщик задач
        logger.info("Прошлые задачи планировщика были очищены")

    scheduler.start()
    logger.info(f"Планировщик заданий {scheduler} запущен")
    logger.info("Все предыдущие задачи планировщика были удалены")


async def load_json(path: str):
    """
    Эта функция загружает календарь нерабочих дней в формате JSON.
    Файл должен быть указан в переменной окружения 'JSON_PATH'.
    """
    async with aiofiles.open(path, mode='r') as json_file:
        content = await json_file.read()
        result = json.loads(content)
        return result
