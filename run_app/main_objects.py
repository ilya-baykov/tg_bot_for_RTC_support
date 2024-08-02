import logging
import json
import aiofiles
from os import environ
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.DataBase import DataBase

logger = logging.getLogger(__name__)

db = DataBase()
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")  # Создание планировщика задач

# session = AiohttpSession(proxy='http://pxs.rt.ru:3128')
# bot = Bot(token=environ.get('TOKEN', 'define me!'), session=session)


bot = Bot(token=environ.get('TOKEN', 'define me!'))


async def load_json(path: str):
    """
    Эта функция загружает календарь нерабочих дней в формате JSON.
    Файл должен быть указан в переменной окружения 'JSON_PATH'.
    """
    async with aiofiles.open(path, mode='r') as json_file:
        content = await json_file.read()
        result = json.loads(content)
        return result
