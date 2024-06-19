from os import environ

from aiogram import Bot

employees_db_update = True

bot = Bot(token=environ.get('TOKEN', 'define me!'))
