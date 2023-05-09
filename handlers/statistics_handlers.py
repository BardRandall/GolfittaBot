from aiogram import Dispatcher, types

from utils import db_utils, strings, states, markups


async def entry_point(message: types.Message):
    pass


async def cmd_start(message: types.Message):
    pass


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
