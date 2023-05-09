from aiogram import executor
from dotenv import load_dotenv

load_dotenv()

from init import dp, on_startup

if __name__ == '__main__':
    executor.start_polling(dp)
    # executor.start_webhook(
    #     dp, on_startup=on_startup, webhook_path=config.WEBHOOK_PATH, host=config.SERVER_HOST, port=config.WEBHOOK_PORT
    # )
