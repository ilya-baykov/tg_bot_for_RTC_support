from aiogram import Bot, Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from database.Database import DataBase
from database.Database import EmployeesDB

start_router = Router()

employees = EmployeesDB(DataBase())


@start_router.message(CommandStart())
async def register_user(message: Message):
    await employees.create_new_employer(telegram_id=message.from_user.id, telegram_username=message.from_user.username,
                                        fullname=message.from_user.full_name)

    await message.answer(
        f"{message.from_user.full_name}, Вы успешно зарегистрировались ! \nВаш ID в базе данных: {message.from_user.id}"
        f"\nВаш никнейм в базе данных: {message.from_user.username}")


def register_start_handlers(dp):
    dp.include_router(start_router)
