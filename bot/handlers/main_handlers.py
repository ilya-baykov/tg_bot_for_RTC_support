from aiogram import Dispatcher


def register_all_handlers(dp: Dispatcher) -> None:
    handlers = (

        # Тут будут другие обработчики
    )
    for handler in handlers:
        handler(dp)
