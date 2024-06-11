from bot.handlers.handlers_router import router
from aiogram import Bot, Dispatcher

from bot.misc.env import TgKeys

# from handlers.start_handler import register_start_handlers
# from handlers.choice_game_handler import register_choice_game_handlers
# from handlers.dice_game_handler import register_dice_game_handlers
# from handlers.blackjack_game_handler import register_blackjack_game_handlers


dp = Dispatcher()
bot = Bot(token=TgKeys.TOKEN)


async def start_bot():
    dp.include_router(router)

    # Регистрация обработчиков
    # register_start_handlers(dp)
    # register_choice_game_handlers(dp)
    # register_dice_game_handlers(dp)
    # register_blackjack_game_handlers(dp)

    await dp.start_polling(bot)
