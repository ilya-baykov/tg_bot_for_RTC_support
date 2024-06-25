import re

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ChatPermissions

from ThrottlingMiddleware import ThrottlingMiddleware
from database.CRUD.сreate import employees_reader, EmployeesCreator, UserAccessCreator
from handlers.start.keyboard import keyboard
from handlers.start.filter import IsTrueContact, UserInBanList
from handlers.start.state import UserRegistration

start_router = Router()
start_router.message.middleware(ThrottlingMiddleware(limit=10))

registration_router = Router()


@registration_router.message(UserInBanList())
async def block_user(message: Message):
    # Для игнорирования запросов от заблокированных пользователей
    pass


@start_router.message(CommandStart())
async def start_register_user(message: Message, state: FSMContext):
    employee = await employees_reader.get_employee_by_telegram_id_or_username(telegram_id=str(message.from_user.id))
    if employee:
        await message.answer(
            f"Здравствуй,{employee.name}.Бот запущен.\nВы уже были успешно зарегистрированы")
    else:
        await message.answer(f"Здравствуй,{message.from_user.username}.\nВведите ваш номер телефона для регистрации.",
                             reply_markup=keyboard)
        await state.set_state(UserRegistration.input_phone)


@registration_router.message(UserRegistration.input_phone, F.contact, IsTrueContact())
async def take_true_contact(message: Message, state: FSMContext):
    # Создаем запись в таблице user_access
    await UserAccessCreator.create_new_user(telegram_id=str(message.from_user.id))

    # Приводим номер к единому формату
    phone = re.sub(r'^\+?7', '8', message.contact.phone_number)

    employee = await employees_reader.get_employee_by_phone(phone_number=phone)
    if employee:
        await EmployeesCreator().create_new_employees(name=employee.fullname,
                                                      telegram_username=message.from_user.username,
                                                      telegram_id=message.from_user.id)
        await message.answer(f"{employee.fullname}, вы успешно зарегистрировались в этом чат-боте.")
        await state.clear()
    else:
        await message.answer(
            f"{message.contact.phone_number} - этот номер не найден в базе. ")


@registration_router.message(UserRegistration.input_phone, F.contact)
async def get_false_contact(message: Message):
    await message.answer("Это не ваш контакт")


def register_start_handlers(dp):
    dp.include_router(start_router)
    dp.include_router(registration_router)
