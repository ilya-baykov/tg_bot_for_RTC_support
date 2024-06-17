from os import environ

from aiogram import Dispatcher, Bot
import asyncio
import platform

from database.Database import DataBase, InputDB, EmployeesDB, ProcessDB, NotificationDB
from handlers.start.start import register_start_handlers
from handlers.send_task_notifications.send_task_notifications import add_jobs

# Установите политику цикла событий для Windows
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

bot = Bot(token=environ.get('TOKEN', 'define me!'))
dp = Dispatcher()
db = DataBase()
inputdb, processesdb = InputDB(db), ProcessDB(db)


async def start():
    try:
        # await db.create_db()
        tasks = await inputdb.get_tasks()
        processes = await processesdb.create_new_processes(tasks, db)

        await add_jobs(bot, processes)

        # Регистрация обработчиков
        register_start_handlers(dp)

        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
# 2024-06-14 02:10:10
