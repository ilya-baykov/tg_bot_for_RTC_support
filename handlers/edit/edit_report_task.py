import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database.CRUD.read import ActionsTodayReader, EmployeesReader, ReportReader
from database.CRUD.update import ReportUpdater
from database.enums import FinalStatus
from handlers.edit.keyboard import inline_today, TaskInfo
from handlers.filters_general import RegisteredUser
from sent_task_to_emploeyee.keyboard import keyboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

edit_router = Router()


class EditState(StatesGroup):
    on_edit = State()
    write_comment = State()


@edit_router.message(RegisteredUser(), Command('edit'))
async def edit_task(message: Message, state: FSMContext):
    employee = await EmployeesReader().get_employee_by_telegram_id_or_username(telegram_id=str(message.from_user.id))

    last_tasks = await ActionsTodayReader().get_completed_actions_by_employee_id(employee.id)

    message_text = 'Выбери процесс,который хочешь редактировать' if last_tasks else "Сегодня вы еще не обработали ни одного действия"

    await message.reply(text=message_text, reply_markup=await inline_today(last_tasks))


@edit_router.callback_query(TaskInfo.filter())
async def process_task_selection(callback_query: CallbackQuery, callback_data: TaskInfo, state: FSMContext):
    await callback_query.answer()
    await state.set_state(EditState.on_edit)

    # Сохраняем номер задач для редактирования
    await state.update_data(task_id=callback_data.task_id)

    await callback_query.message.answer(
        text=f"Отредактируйте задачу {callback_data.task_id}",
        reply_markup=keyboard
    )


@edit_router.message(EditState.on_edit, F.text.in_({"Выполнено", "Не выполнено"}))
async def test(message: Message, state: FSMContext):
    await state.set_state(EditState.write_comment)
    if message.text == "Выполнено":
        await state.update_data({"status": FinalStatus.successfully})
    elif message.text == "Не выполнено":
        await state.update_data({"status": FinalStatus.failed})
    await message.answer("Напиши комментарий")


@edit_router.message(EditState.write_comment)
async def test_2(message: Message, state: FSMContext):
    user_data = await state.get_data()
    task_id = user_data.get("task_id")
    status = user_data.get("status")
    report = await ReportReader().get_report_by_actions_id(int(task_id))
    await ReportUpdater().update_params(report, status=status, comment=message.text)
    await state.clear()
    await message.answer("Изменеия успешно сохранились в таблицу.")


def register_edit_handlers(dp):
    dp.include_router(edit_router)
