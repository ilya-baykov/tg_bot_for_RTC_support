from os import environ

from aiogram import Dispatcher, Bot
import asyncio
import platform

from database.Database import DataBase, InputDB, EmployeesDB, ProcessDB, NotificationDB
from handlers.start.start import register_start_handlers
from handlers.user_answer.user_answer import register_user_response
from handlers.send_task_notifications.adding_messages_queue import *

from global_variables import bot

# Установите политику цикла событий для Windows
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# bot = Bot(token=environ.get('TOKEN', 'define me!'))
dp = Dispatcher()
db = DataBase()
inputdb, processesdb = InputDB(db), ProcessDB(db)


# async def special_function():
#     while True:
#         # Ваш код, который должен выполняться постоянно
#         print("Специальная функция выполняется...")
#         await asyncio.sleep(10)  # Пример: выполняется каждые 10 секунд


async def start():
    try:
        # await db.reset_database() # Очищает БД
        # await db.create_db() # Создает все модели в БД
        tasks = await inputdb.get_tasks()  # Получаем все текущие задачи
        await processesdb.create_new_processes(tasks, db)  # Создаем новые процессы
        await  getting_employees_current_task()

        # Регистрация обработчиков
        register_start_handlers(dp)
        register_user_response(dp)

        # Запуск специальной функции параллельно
        # asyncio.create_task(special_function())
        # special_task = asyncio.create_task(special_function())

        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
# 2024-06-14 02:10:10
