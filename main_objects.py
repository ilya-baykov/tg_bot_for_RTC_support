from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.DataBase import DataBase

db = DataBase()
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")  # Создание планировщика задач
