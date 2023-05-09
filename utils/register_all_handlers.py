from aiogram import Dispatcher

from handlers import start_handlers, sportsman_menu_handlers, trainer_menu_handlers, list_games_handlers, \
    add_game_handlers


def register_all_handlers(dp: Dispatcher):
    start_handlers.register_handlers(dp)
    sportsman_menu_handlers.register_handlers(dp)
    trainer_menu_handlers.register_handlers(dp)
    list_games_handlers.register_handlers(dp)
    add_game_handlers.register_handlers(dp)
