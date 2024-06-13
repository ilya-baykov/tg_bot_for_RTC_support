from os import environ

from aiogram import Dispatcher, Bot, F
import asyncio
import platform
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from database.Database import Database
from handlers.start.start import register_start_handlers

# Установите политику цикла событий для Windows
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

bot = Bot(token=environ.get('TOKEN', 'define me!'))
dp = Dispatcher()


async def start_bot(bot: Bot):
    await bot.send_message(chat_id="793353522", text="Бот запушен :)")


dp.startup.register(start_bot)


async def start():
    try:
        db = Database()
        # await db.create_db()
        await db.select_future_tasks()
        # Регистрация обработчиков
        register_start_handlers(dp)

        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
