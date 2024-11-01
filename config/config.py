
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Telegram Configs
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    # LLM Configs
    LLM_TOKEN = os.getenv("GROQ_TOKEN")
    LLM_MODEL = os.getenv("LLM_MODEL")
    LLM_TEMPERATURE = 0.0

    # DB Configs
    DB_SERVICE_URI = os.getenv("DB_SERVICE_URI")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    # App config
    MAX_ITEM_LIMIT = 5
    CRON_INTERVAL = 10
