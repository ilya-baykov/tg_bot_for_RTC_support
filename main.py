from os import environ

from aiogram import Dispatcher, Bot, F
import asyncio
import platform

from database.Database import Database
from handlers.send_task_notifications.TaskManager import TaskManager
from handlers.start.start import register_start_handlers
from handlers.send_task_notifications.send_task_notifications import add_jobs
# from handlers.send_task_notifications.send_task_notifications import register_send_task_handlers
from handlers.user_answer.user_answer import register_user_response

# Установите политику цикла событий для Windows
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

bot = Bot(token=environ.get('TOKEN', 'define me!'))
dp = Dispatcher()


async def start():
    try:
        db = Database()
        tasks = await db.select_future_tasks()
        await db.create_processes(tasks)
        processes = await db.get_all_processes()

        await add_jobs(bot, processes)
        # await db.create_db()
        # tasks = await db.select_future_tasks()  # Получаем задачи один раз при запуске

        # Регистрация обработчиков
        register_start_handlers(dp)
        # register_send_task_handlers(dp, bot, tasks)
        # register_user_response(dp)

        task_manager = TaskManager(bot, db)
        await task_manager.load_tasks()
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
# 2024-06-14 02:10:10
