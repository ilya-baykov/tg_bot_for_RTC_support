from aiogram import Bot, Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ContentType
from database_old.Database import DataBase
from database_old.Database import EmployeesDB
from database_old.Database import EmployeePhonesDB
from handlers.start.keyboard import keyboard
from handlers.start.filter import IsTrueContact
from handlers.user_answer.state import UserResponse

start_router = Router()

db = DataBase()
employees = EmployeesDB(db)
employees_phones = EmployeePhonesDB(db)


class UserRegistration(StatesGroup):
    input_phone = State()


@start_router.message(CommandStart())
async def start_register_user(message: Message, state: FSMContext):
    employee = await employees.get_employee_by_telegram_id(message.from_user.id)
    if employee:
        await message.answer(
            f"Здравствуй,{employee.name}.Бот запущен.\nВы уже были успешно зарегистрированы")
        await state.set_state(UserResponse.wait_message)
    else:
        await message.answer(f"Здравствуй,{message.from_user.username}.\nВведите ваш номер телефона для регистрации.",
                             reply_markup=keyboard)
        await state.set_state(UserRegistration.input_phone)


@start_router.message(UserRegistration.input_phone, F.contact, IsTrueContact())
async def take_true_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number.replace("+7", "8")
    employee = await employees_phones.get_employee_by_phone(phone_number=phone)
    if employee:
        await employees.create_new_employer(telegram_id=message.from_user.id,
                                            telegram_username=message.from_user.username,
                                            fullname=employee.fullname)
        await message.answer(f"{employee.fullname}, вы успешно зарегистрировались в этом чат-боте.")
        await state.clear()
    else:
        await message.answer(
            f"{message.contact.phone_number} - этот номер не найден в базе. ")


@start_router.message(UserRegistration.input_phone, F.contact)
async def get_false_contact(message: Message):
    await message.answer("Это не ваш контакт")


def register_start_handlers(dp):
    dp.include_router(start_router)
