import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2

import config
from utils import register_all_handlers


async def on_startup(dp: Dispatcher):
    await bot.delete_webhook()
    await bot.set_webhook(config.WEBHOOK_URL)

logging.basicConfig(level=logging.DEBUG)

bot = Bot(config.BOT_TOKEN, parse_mode="html")
dp = Dispatcher(bot, storage=RedisStorage2())

register_all_handlers.register_all_handlers(dp)
