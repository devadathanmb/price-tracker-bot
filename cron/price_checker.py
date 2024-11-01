import datetime
from aiogram.enums import ParseMode
from db.core import get_db
from db.models import TrackedItem, User
from db.repositories.tracked_item import TrackedItemRepository
from db.repositories.user import UserRepository
from scraper.scraper import scraper
from utils.logger import get_logger
from bot import bot

logger = get_logger(__name__)

class PriceAlert:
    """Formats and sends price alert messages."""
    
    @staticmethod
    def format_message(item: TrackedItem, current_price: float) -> str:
        return (
            f"🎉 Price Alert for *{item.name}*!\n\n"
            f"💰 Current Price: *{item.currency} {current_price}*\n"
            f"🎯 Your Target Price: *{item.currency} {item.target_price}*\n\n"
            f"🔗 Check it out here: [Link]({item.link})\n\n"
            f"Act fast before it changes again!"
        )
    
    @staticmethod
    async def send_alert(item: TrackedItem, current_price: float, user_id: int) -> None:
        try:
            message = PriceAlert.format_message(item, current_price)
            await bot.send_message(
                user_id,
                message,
                parse_mode=ParseMode.MARKDOWN
            )
            logger.info(f"Sent price alert to user {user_id} for item {item.name}")
        except Exception as e:
            logger.error(f"Failed to send price alert to user {user_id}: {e}")

class PriceChecker:
    """Handles price checking and updates for tracked items."""
    
    def __init__(self):
        self.user_repository = UserRepository()
        self.tracked_item_repository = TrackedItemRepository()
    
    async def check_all_prices(self) -> None:
        """Check prices for all users' tracked items."""
        logger.info("Starting price check for all users")
        try:
            with get_db() as db:
                users = self.user_repository.get_all(db)
                for user in users:
                    await self._process_user_items(user, db)
            logger.info("Completed price check for all users")
        except Exception as e:
            logger.error(f"Error in price check: {e}")

    async def _process_user_items(self, user: User, db) -> None:
        """Process all tracked items for a specific user."""
        try:
            items = self.tracked_item_repository.get_by_user_id(db, user.id)
            for item in items:
                await self._check_item_price(item, user.id, db)
        except Exception as e:
            logger.error(f"Error processing items for user {user.id}: {e}")

    async def _check_item_price(self, item: TrackedItem, user_id: int, db) -> None:
        """Check and update price for a single item."""
        try:
            latest_data = await scraper.scrape(url=item.link)
            if not latest_data["is_trackable"]:
                logger.warning(f"Item {item.name} is no longer trackable")
                return

            current_price = float(latest_data["price"])
            if current_price < item.target_price:
                logger.info(
                    f"Price drop detected for {item.name}: "
                    f"{item.current_price} -> {current_price}"
                )
                
                # Update item
                self._update_item(item, current_price, db)
                
                # Send alert
                await PriceAlert.send_alert(item, current_price, user_id)
            else:
                # Just update timestamps
                self._update_timestamps(item, db)

        except Exception as e:
            logger.error(f"Error checking price for item {item.name}: {e}")

    def _update_item(self, item: TrackedItem, new_price: float, db) -> None:
        """Update item price and timestamps."""
        try:
            now = datetime.datetime.now(datetime.timezone.utc)
            item.current_price = new_price
            item.last_checked_at = now
            item.updated_at = now
            db.add(item)
        except Exception as e:
            logger.error(f"Error updating item {item.name}: {e}")

    def _update_timestamps(self, item: TrackedItem, db) -> None:
        """Update only item timestamps."""
        try:
            now = datetime.datetime.now(datetime.timezone.utc)
            item.last_checked_at = now
            item.updated_at = now
            db.add(item)
        except Exception as e:
            logger.error(f"Error updating timestamps for item {item.name}: {e}")

# Create singleton instance
price_checker = PriceChecker()

# Main function to be called by the scheduler
async def check_price_drops() -> None:
    """Main entry point for price checking."""
    try:
        await price_checker.check_all_prices()
    except Exception as e:
        logger.error(f"Error in check_price_drops: {e}")
