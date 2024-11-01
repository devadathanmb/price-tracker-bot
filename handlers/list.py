from typing import List
from aiogram.types import Message
from db.core import get_db
from db.repositories.tracked_item import tracked_item_service
from utils.logger import get_logger

logger = get_logger(__name__)

class ListMessages:
    """Messages for the list command flow."""
    
    NO_USER = "Error: Could not identify user."
    
    NO_ITEMS = (
        "You don't have any items currently being tracked.\n"
        "Get started by using the /track command!"
    )
    
    LIST_HEADER = "Here are your tracked items:\n\n"
    
    ERROR = "Sorry, I encountered an error while fetching your items. Please try again later."

    @staticmethod
    def format_item(item) -> str:
        """Format a single tracked item for display."""
        return (
            f"<b>Name:</b> {item.name}\n"
            f"<b>Current Price:</b> {item.currency} {item.current_price:.2f}\n"
            f"<b>Target Price:</b> {item.currency} {item.target_price:.2f}\n"
            f"<b>Link:</b> <a href='{item.link}'>{item.link}</a>\n"
            f"<b>Last Checked:</b> {item.last_checked_at:%Y-%m-%d %H:%M:%S}\n"
            f"<b>Updated:</b> {item.updated_at:%Y-%m-%d %H:%M:%S}\n\n"
            f"<i>---</i>\n\n"
        )

    @staticmethod
    def format_items_list(items: List) -> str:
        """Format the complete list of tracked items."""
        if not items:
            return ListMessages.NO_ITEMS
        
        message = ListMessages.LIST_HEADER
        for item in items:
            message += ListMessages.format_item(item)
        return message

async def command_list_handler(message: Message) -> None:
    """Handle the /list command to show all tracked items for a user."""
    if not message.from_user:
        logger.error("Received message without user information")
        await message.answer(ListMessages.NO_USER)
        return

    user_id = message.from_user.id
    logger.info(f"List command received from user {user_id}")

    try:
        with get_db() as db:
            items = tracked_item_service.repository.get_by_user_id(db, user_id)
            response_msg = ListMessages.format_items_list(items)
            
            await message.answer(
                response_msg,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            
            logger.info(f"Successfully listed {len(items)} items for user {user_id}")
            
    except Exception as e:
        logger.error(f"Error listing items for user {user_id}: {str(e)}")
        await message.answer(ListMessages.ERROR)
