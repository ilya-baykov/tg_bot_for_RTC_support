from aiogram import Bot, Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from database.Database import DataBase
from database.Database import EmployeesDB
from database.Database import EmployeePhonesDB

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
    else:
        await message.answer(f"Здравствуй,{message.from_user.username}.\nВведите ваш номер телефона для регистрации.")
        await state.set_state(UserRegistration.input_phone)


@start_router.message(UserRegistration.input_phone)
async def input_phone_number(message: Message, state: FSMContext):
    employee = await employees_phones.get_employee_by_phone(phone_number=message.text)
    if employee:
        await employees.create_new_employer(telegram_id=message.from_user.id,
                                            telegram_username=message.from_user.username,
                                            fullname=employee.fullname)
        await message.answer(f"{employee.fullname}, вы успешно зарегистрировались в этом чат-боте.")
        await state.clear()
    else:
        await message.answer(
            f"{message.text} - этот номер не найден в базе. Попробуйте ввести только 11 цифр без лищних символов ")


def register_start_handlers(dp):
    dp.include_router(start_router)
