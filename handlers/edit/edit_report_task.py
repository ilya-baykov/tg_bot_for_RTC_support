import logging
from datetime import datetime, timedelta
from typing import Tuple, Union

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.CRUD.read import ActionsTodayReader, EmployeesReader
from handlers.edit.keyboard import inline_today

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

edit_router = Router()


@edit_router.message(Command('edit'))
async def edit_task(message: Message):
    employee = await EmployeesReader().get_employee_by_telegram_id_or_username(telegram_id=str(message.from_user.id))
    if employee:
        last_tasks = await ActionsTodayReader().get_completed_actions_by_employee_id(employee.id)

        message_text = 'Выбери процесс,который хочешь редактировать' if last_tasks else "Сегодня вы еще не обработали ни одного действия"

        await message.reply(text=message_text, reply_markup=await inline_today(last_tasks))
    else:
        await message.reply(text="Вам недоступен этот функционал, попробуйте зарегистрироваться")


def register_edit_handlers(dp):
    dp.include_router(edit_router)
