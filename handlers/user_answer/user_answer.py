from aiogram import Router, F
from aiogram.types import Message

user_answer = Router()


@user_answer.message(F.text == "Выполнено")
async def user_response(message: Message):
    await message.answer("Отлично, мы записали это в БД")


@user_answer.message(F.text == "Не выполнено")
async def user_response(message: Message):
    await message.answer("Напиши комментарий")


def register_user_response(dp):
    dp.include_router(user_answer)
