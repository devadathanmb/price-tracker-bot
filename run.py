import asyncio
from aiogram import Dispatcher
from handlers.register_handlers import register_handlers
from bot import bot
from cron.price_checker import check_price_drops
from utils.logger import get_logger
from config import Config

logger = get_logger(__name__)

dp = Dispatcher()

async def periodic_price_check():
    while True:
        try:
            logger.info("Price check sleeping..")
            await asyncio.sleep(Config.CRON_INTERVAL)
            logger.info("Running price check...")
            await check_price_drops()
        except Exception as e:
            logger.error(f"Error in periodic price check: {e}")
            # Sleep a bit before retrying after error
            await asyncio.sleep(60)

async def main() -> None:
    try:
        register_handlers(dp)
        # Start the periodic price check task
        asyncio.create_task(periodic_price_check())
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
