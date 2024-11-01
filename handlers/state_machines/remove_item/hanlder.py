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
remove_item_router = Router()


class RemoveItemStates(StatesGroup):
    remove_item_id = State()
    remove_another = State()


class RemoveMessages:
    """Messages for the remove item flow."""

    NO_USER = "Could not identify user."

    NO_ITEMS = "You have no items to remove."

    ITEM_REMOVED = "Item removed. Do you want to remove another item?"

    REMOVE_SUCCESS = "Item removed successfully"

    REMOVE_ERROR = "Item not found or you don't have permission"

    PROCESS_COMPLETE = "Removal process completed"

    START_AGAIN = "You can start again using /remove."

    ERROR = "Sorry, something went wrong. Please try again."

    @staticmethod
    def format_items_list(items: list) -> str:
        """Format the list of items for display."""
        if not items:
            return RemoveMessages.NO_ITEMS

        message = "Choose an item to remove:\n\n"
        for index, item in enumerate(items, 1):
            message += (
                f"<b>{index}. {item.name}</b>\n\n"
                f"🔗 <a href='{item.link}'>Link</a>\n\n"
                f"💰 Current Price: {item.currency} {item.current_price}\n\n"
                f"🎯 Target Price: {item.currency} {item.target_price}\n\n"
                f"🕒 Last Checked: {item.last_checked_at}\n\n\n"
            )
        return message


class RemoveKeyboardFactory:
    """Creates keyboards for the remove item flow."""

    @staticmethod
    def create_items_keyboard(items: list) -> InlineKeyboardBuilder:
        """Create keyboard with numbered buttons for items."""
        kb = InlineKeyboardBuilder()
        for index, item in enumerate(items, 1):
            kb.button(text=str(index), callback_data=str(item.id))
        return kb.as_markup()

    @staticmethod
    def create_another_keyboard() -> InlineKeyboardBuilder:
        """Create keyboard for asking to remove another item."""
        kb = InlineKeyboardBuilder()
        kb.button(text="Yes", callback_data="remove_another_yes")
        kb.button(text="No", callback_data="remove_another_no")
        return kb.as_markup()


@remove_item_router.message(Command("remove"))
async def command_remove_handler(message: Message, state: FSMContext) -> None:
    """Handle the /remove command."""
    if not message.from_user:
        logger.error("Received message without user information")
        await message.answer(RemoveMessages.NO_USER)
        return

    user_id = message.from_user.id
    logger.info(f"Remove command received from user {user_id}")

    try:
        with get_db() as db:
            items = tracked_item_service.repository.get_by_user_id(db, user_id)

            if not items:
                await message.answer(RemoveMessages.NO_ITEMS)
                return

            items_message = RemoveMessages.format_items_list(items)
            keyboard = RemoveKeyboardFactory.create_items_keyboard(items)

            await message.answer(
                items_message, parse_mode="HTML", reply_markup=keyboard
            )
            await state.set_state(RemoveItemStates.remove_item_id)

    except Exception as e:
        logger.error(f"Error in remove handler for user {user_id}: {e}")
        await message.answer(RemoveMessages.ERROR)


@remove_item_router.callback_query(
    RemoveItemStates.remove_item_id, F.data.regexp(r"^\d+$")
)
async def remove_item_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle item removal selection."""
    if not callback.from_user:
        return

    user_id = callback.from_user.id
    item_id = int(callback.data)

    try:
        with get_db() as db:
            if tracked_item_service.repository.delete_by_id(
                db, item_id=item_id, user_id=user_id
            ):
                await callback.answer(RemoveMessages.REMOVE_SUCCESS)
            else:
                await callback.answer(RemoveMessages.REMOVE_ERROR)
                return

        keyboard = RemoveKeyboardFactory.create_another_keyboard()
        await callback.message.edit_text(
            RemoveMessages.ITEM_REMOVED, reply_markup=keyboard
        )
        await state.set_state(RemoveItemStates.remove_another)

    except Exception as e:
        logger.error(f"Error removing item {item_id} for user {user_id}: {e}")
        await callback.message.edit_text(RemoveMessages.ERROR)
        await state.clear()


@remove_item_router.callback_query(
    RemoveItemStates.remove_another, F.data == "remove_another_yes"
)
async def yes_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle 'Yes' response to remove another item."""
    await callback.answer()
    await command_remove_handler(callback.message, state)


@remove_item_router.callback_query(
    RemoveItemStates.remove_another, F.data == "remove_another_no"
)
async def no_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle 'No' response to remove another item."""
    await callback.answer(RemoveMessages.PROCESS_COMPLETE)
    await callback.message.edit_text(RemoveMessages.START_AGAIN)
    await state.clear()


@remove_item_router.error()
async def error_handler(event: ErrorEvent) -> None:
    """Handle errors in the remove item flow."""
    logger.error(f"Error in remove handler: {event.exception}", exc_info=True)

    try:
        if event.update.message:
            await event.update.message.answer(RemoveMessages.ERROR)
        elif event.update.callback_query:
            await event.update.callback_query.message.edit_text(RemoveMessages.ERROR)
    except Exception as e:
        logger.error(f"Error in error handler: {e}")
