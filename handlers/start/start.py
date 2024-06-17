from aiogram import Bot, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.Database import Database

start_router = Router()

db = Database()


@start_router.message(CommandStart())
async def register_user(message: Message):
    print(message)
    await db.add_employees(telegram_id=message.from_user.id, telegram_username=message.from_user.username,
                           fullname=message.from_user.full_name)
    await message.answer(
        f"{message.from_user.full_name}, Вы успешно зарегистрировались ! \nВаш ID в базе данных: {message.from_user.id}"
        f"\nВаш никнейм в базе данных: {message.from_user.username}")


def register_start_handlers(dp):
    dp.include_router(start_router)
