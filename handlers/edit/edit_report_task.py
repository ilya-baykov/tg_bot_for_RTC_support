import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from database.CRUD.read import ActionsTodayReader, EmployeesReader
from handlers.edit.keyboard import inline_today, TaskInfo
from handlers.filters_general import RegisteredUser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

edit_router = Router()


class EditState(StatesGroup):
    wait_edit = State()
    on_edit = State()


@edit_router.message(RegisteredUser(), Command('edit'))
async def edit_task(message: Message, state: FSMContext):
    employee = await EmployeesReader().get_employee_by_telegram_id_or_username(telegram_id=str(message.from_user.id))

    last_tasks = await ActionsTodayReader().get_completed_actions_by_employee_id(employee.id)

    message_text = 'Выбери процесс,который хочешь редактировать' if last_tasks else "Сегодня вы еще не обработали ни одного действия"

    await message.reply(text=message_text, reply_markup=await inline_today(last_tasks))


@edit_router.callback_query(TaskInfo.filter())
async def test_cb_data(callback_query: CallbackQuery, callback_data: TaskInfo):
    await callback_query.answer(
        text=("Проверка определения задачи"
              f"{callback_data.task_id}")
    )


def register_edit_handlers(dp):
    dp.include_router(edit_router)
