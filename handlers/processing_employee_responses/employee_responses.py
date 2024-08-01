import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.CRUD.read import ClearInputTableReader, ProcessDirectoryReader
from database.models import ClearInputData, ProcessDirectory
from handlers.add_journal_entry.state import AddOperationLogState
from handlers.filters_general import RegisteredUser
from handlers.processing_employee_responses.keyboard import yes_or_no_keyboard
from middlewares.ThrottlingMiddleware import ThrottlingMiddleware
from database.enums import FinalStatus
from handlers.processing_employee_responses.state import UserResponse
from utility.ActionManager import ActionManager, AfterFillingReportReturn

logger = logging.getLogger(__name__)

user_answer = Router()
user_answer.message.middleware(ThrottlingMiddleware(limit=2))


@user_answer.message(RegisteredUser(), F.text == "Выполнено")
async def user_response(message: Message, state: FSMContext):
    result: AfterFillingReportReturn = await ActionManager.filling_out_report(
        user_telegram_id=str(message.from_user.id),
        status=FinalStatus.successfully,
        comment="")

    await message.answer(result.message)


@user_answer.message(RegisteredUser(), F.text == "Не выполнено")
async def user_response(message: Message, state: FSMContext):
    await state.set_state(UserResponse.comment)
    await message.answer("Напиши комментарий")


@user_answer.message(F.text == "Да", UserResponse.comment)
async def start_add_journal_entry(message: Message, state: FSMContext):
    # Получаем данные по процессу и сотруднику ТП
    state_data = await state.get_data()
    process: ClearInputData = await ClearInputTableReader.get_input_task_by_id(
        state_data["after_filling"].sent_process.input_data_id)
    process: ProcessDirectory = await ProcessDirectoryReader().get_process(process.process_name.strip())
    await state.update_data({"employee_name": state_data["after_filling"].employee.name, "process": process})

    await message.answer("Введите описание ошибки")
    await state.set_state(AddOperationLogState.enter_error_description)


@user_answer.message(F.text == "Нет", UserResponse.comment)
async def end_report_entry(message: Message, state: FSMContext):
    state_data = await state.get_data()
    if state_data.get('change_status'):
        employee, sent_process = await ActionManager.check_user_response(str(message.from_user.id))
        await ActionManager.update_status(employee, sent_process)
    await state.clear()


@user_answer.message(UserResponse.comment)
async def write_user_comment(message: Message, state: FSMContext):
    result: AfterFillingReportReturn = await ActionManager.filling_out_report(
        user_telegram_id=str(message.from_user.id),
        status=FinalStatus.failed,
        comment=message.text,
        change_status=False)

    await message.answer(result.message)
    await message.answer("Хотите добавить запись в журнал эксплуатации ?", reply_markup=yes_or_no_keyboard)
    await state.update_data({"change_status": True, "after_filling": result})


def register_user_response(dp):
    dp.include_router(user_answer)
