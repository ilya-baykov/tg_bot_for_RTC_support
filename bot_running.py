from os import environ

from aiogram import Dispatcher, Bot

from handlers.processing_employee_responses.employee_responses import register_user_response
from handlers.start.registration import register_start_handlers

bot = Bot(token=environ.get('TOKEN', 'define me!'))
dp = Dispatcher()


async def start_bot():
    # Регистрация обработчиков

    register_start_handlers(dp)  # Стартовый обработчик
    register_user_response(dp)  # Обработчик ответов сотрудников

    await dp.start_polling(bot, skip_updates=True)
