from aiogram import Dispatcher, Bot, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from handlers.send_task_notifications.keyboard import keyboard

user_answer = Router()

print("Ты тут")


@user_answer.message(F.text == "Выполнено")
async def user_response(message: Message):
    await message.answer("Отлично, мы записали это в БД")


@user_answer.message(F.text == "Не выполнено")
async def user_response(message: Message):
    await message.answer("Напиши комментарий")


def register_user_response(dp):
    dp.include_router(user_answer)
