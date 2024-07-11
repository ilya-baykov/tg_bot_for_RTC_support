import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from handlers.filters_general import RegisteredUser
from middlewares.ThrottlingMiddleware import ThrottlingMiddleware
from database.enums import FinalStatus
from handlers.processing_employee_responses.state import UserResponse
from utility.ActionManager import ActionManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_answer = Router()
user_answer.message.middleware(ThrottlingMiddleware(limit=2))


@user_answer.message(RegisteredUser(), F.text == "Выполнено")
async def user_response(message: Message, state: FSMContext):
    text_message = await ActionManager.filling_out_report(
        user_telegram_id=str(message.from_user.id),
        status=FinalStatus.successfully,
        comment=""
    )
    await message.answer(text_message)


@user_answer.message(RegisteredUser(), F.text == "Не выполнено")
async def user_response(message: Message, state: FSMContext):
    await state.set_state(UserResponse.comment)
    await message.answer("Напиши комментарий")


@user_answer.message(RegisteredUser(), UserResponse.comment)
async def write_user_comment(message: Message, state: FSMContext):
    text_message = await ActionManager.filling_out_report(
        user_telegram_id=str(message.from_user.id),
        status=FinalStatus.failed,
        comment=message.text
    )
    await state.set_state(UserResponse.wait_message)
    await message.answer(text_message)


def register_user_response(dp):
    dp.include_router(user_answer)
