import os

# Bot config
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Webhook config
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PORT = os.getenv("WEBHOOK_PORT")
WEBHOOK_PATH = f"/{BOT_TOKEN}"
WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH
SERVER_HOST = "0.0.0.0"

# DB config
DB_HOST = "mongodb://localhost:27017/"
DB_NAME = "golfitta"

# Colors
COLOR_GREEN = "#90EE90"
COLOR_WHITE = "w"
COLOR_RED = "#FF7276"
