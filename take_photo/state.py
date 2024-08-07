import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.models import Report
from run_app.main_objects import bot, db

photo = Router()


@photo.message(F.photo)
async def get_photo_by_user(message: Message, state: FSMContext):
    await bot.download(
        message.photo[-1],
        destination=f"C:\\Users\\ilyab\\OneDrive\\Рабочий стол\\tmp\\{message.photo[-1].file_id}.jpg"
    )
    photo = message.photo[-1]  # Получаем фото с наибольшим разрешением
    file_id = photo.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    # Скачиваем файл
    file_data = await bot.download_file(file_path)
    # Сохраняем данные в БД
    async with db.Session() as request:
        request.add(Report(
            process_name="Example Process",
            action_description="Example Action",
            expected_dispatch_time=datetime.datetime.now(),
            actual_dispatch_time=datetime.datetime.now(),
            employee_response_time=datetime.datetime.now(),
            elapsed_time=datetime.timedelta(seconds=0),
            status="Pending",
            comment="Example Comment",
            photo=file_data.read()  # Сохраняем бинарные данные изображения
        ))
        await request.commit()

    await message.reply("Фото сохранено!")


def register_photo_by_user(dp):
    dp.include_router(photo)
