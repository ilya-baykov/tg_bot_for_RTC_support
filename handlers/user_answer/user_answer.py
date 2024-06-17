from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from handlers.user_answer.states import UserResponse
from database.Database import NotificationDB
from .MyFilters import MyFilter

user_answer = Router()


@user_answer.message(MyFilter())
async def test_my_filter(message: Message, state: FSMContext):
    print("Да,он сработал")
    await message.answer("ДА!")
    await state.set_state(UserResponse.response)
    # await message.answer("Да, он сработал")


@user_answer.message(UserResponse.response)
async def user_response(message: Message, state: FSMContext):
    await state.set_state(UserResponse.task_send)
    await message.answer(f"Отлично, мы записали это в БД")


@user_answer.message(F.text == "Не выполнено")
async def user_response(message: Message, state: FSMContext):
    await state.set_state(UserResponse.comment)
    await message.answer("Напиши комментарий")


@user_answer.message(UserResponse.comment)
async def write_user_comment(message: Message, state: FSMContext):
    await message.answer("Спасибо за уточнение, мы записали это в БД")
    await state.set_state(UserResponse.task_send)


def register_user_response(dp):
    dp.include_router(user_answer)
