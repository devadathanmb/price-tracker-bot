from aiogram.types import Message
from db.core import get_db
from db.repositories.user import user_service
from utils.logger import get_logger

logger = get_logger(__name__)

class StartMessages:
    """Message templates for start command."""
    
    WELCOME = (
        "Welcome to the Price Tracker Bot! 🤖\n\n"
        "I can help you track prices of your favorite products. "
        "Here's what you can do:\n\n"
        "🔸 /track - Start tracking a new product\n"
        "🔸 /list - View your tracked items\n"
        "🔸 /remove - Remove items from tracking\n"
        "🔸 /help - Get detailed instructions\n\n"
        "Let's start tracking! Use /track to add your first item."
    )
    
    SETUP = "Setting up your account... Please wait a moment. ⌛"
    ERROR = "Sorry, I encountered an error. Please try again with /start"

async def command_start_handler(message: Message) -> None:
    """Handle the /start command."""
    if not message.from_user:
        logger.error("Received message without user information")
        await message.answer("Error: Could not identify user.")
        return
    
    user_id = message.from_user.id
    logger.info(f"Start command received from user {user_id}")
    
    try:
        await message.answer(StartMessages.SETUP)
        
        with get_db() as db:
            await user_service.ensure_user_exists(db, user_id)
            logger.info(f"User {user_id} setup completed")
            
            await message.answer(StartMessages.WELCOME)
            
    except Exception as e:
        logger.error(f"Error in start command for user {user_id}: {str(e)}")
        await message.answer(StartMessages.ERROR)
