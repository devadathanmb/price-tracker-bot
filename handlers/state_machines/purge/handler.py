from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ErrorEvent
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from db.core import get_db
from db.repositories.tracked_item import tracked_item_service
from utils.logger import get_logger

logger = get_logger(__name__)

# Initialize router
purge_router = Router()

class PurgeStates(StatesGroup):
    awaiting_confirmation = State()

class PurgeMessages:
    CONFIRMATION = (
        "⚠️ <b>Warning!</b>\n\n"
        "You are about to delete <b>ALL</b> your tracked items. "
        "This action cannot be undone.\n\n"
        "Are you sure you want to continue?"
    )
    
    IN_PROGRESS = "🗑 Purging all tracked items... Please wait..."
    
    SUCCESS = (
        "✅ Purge completed successfully!\n\n"
        "All your tracked items have been removed. "
        "Use /track to start tracking new items."
    )
    
    ERROR = (
        "❌ Sorry, something went wrong while purging your items.\n"
        "Please try again later."
    )

class PurgeKeyboardFactory:
    @staticmethod
    def get_confirmation_keyboard() -> InlineKeyboardBuilder:
        kb = InlineKeyboardBuilder()
        kb.button(
            text="Yes, delete everything",
            callback_data="confirm_purge"
        )
        kb.button(
            text="No, keep my items",
            callback_data="cancel_purge"
        )
        return kb.as_markup()

@purge_router.message(Command("purge"))
async def command_purge_handler(message: Message, state: FSMContext) -> None:
    """Handle the initial /purge command."""
    if not message.from_user:
        logger.error("Received message without user information")
        await message.answer("Error: Could not identify user.")
        return

    user_id = message.from_user.id
    logger.info(f"Purge command received from user {user_id}")

    await message.answer(
        PurgeMessages.CONFIRMATION,
        reply_markup=PurgeKeyboardFactory.get_confirmation_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(PurgeStates.awaiting_confirmation)

@purge_router.callback_query(
    PurgeStates.awaiting_confirmation,
    F.data.in_(["confirm_purge", "cancel_purge"])
)
async def process_purge_confirmation(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle the purge confirmation response."""
    user_id = callback.from_user.id
    
    if callback.data == "cancel_purge":
        await callback.message.edit_text("Purge cancelled. Your items are safe.")
        await state.clear()
        return

    try:
        await callback.message.edit_text(PurgeMessages.IN_PROGRESS)
        
        with get_db() as db:
            items_deleted = tracked_item_service.repository.delete_all_by_user(db, user_id)
            logger.info(f"Successfully purged {items_deleted} items for user {user_id}")
            
            await callback.message.edit_text(PurgeMessages.SUCCESS)
            
    except Exception as e:
        logger.error(f"Error purging items for user {user_id}: {str(e)}")
        await callback.message.edit_text(PurgeMessages.ERROR)
    finally:
        await state.clear()

@purge_router.error()
async def error_handler(event: ErrorEvent) -> None:
    """
    Handle errors in the purge flow.
    Uses aiogram's ErrorEvent for proper error handling.
    """
    logger.error(f"Error in purge handler: {event.exception}", exc_info=True)
    
    try:
        # Try to get the chat where the error occurred
        if event.update.message:
            await event.update.message.answer(PurgeMessages.ERROR)
        elif event.update.callback_query:
            await event.update.callback_query.message.edit_text(PurgeMessages.ERROR)
    except Exception as e:
        logger.error(f"Error in error handler: {e}")
