from os import environ

from aiogram import Dispatcher, Bot

bot = Bot(token=environ.get('TOKEN', 'define me!'))
dp = Dispatcher()


async def start_bot():
    # Регистрация обработчиков
    # Стартовый обработчик
    # Обработчик ответов сотрудников
    pass
