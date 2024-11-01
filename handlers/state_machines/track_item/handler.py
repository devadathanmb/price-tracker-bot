from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ErrorEvent
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from db.core import get_db
from db.repositories.tracked_item import tracked_item_service
from scraper.scraper import scraper
from utils.logger import get_logger
import validators

logger = get_logger(__name__)

# Initialize router
track_item_router = Router()

class TrackStates(StatesGroup):
    product_link = State()
    target_price = State()
    confirmation = State()

class TrackMessages:
    REQUEST_LINK = "Please send the link of the product you want to track."
    
    PROCESSING = "Please wait while I check if this product is trackable..."
    
    INVALID_URL = "Please provide a valid product URL."
    
    INVALID_PRICE = "Please provide a valid number for the price."
    
    PRICE_TOO_LOW = "Price must be greater than 0."
    
    CANNOT_TRACK = "Sorry, I cannot track this product. Please try a different link."

    CAN_TRACK = "Yay!! I can track this!"
    
    REQUEST_TARGET = "Now, please send your target price."
    
    LIMIT_REACHED = "You've reached the maximum number of items you can track. Please remove some items first."
    
    ADDING_ITEM = "Adding item to watchlist... Please wait..."
    
    SUCCESS = "Successfully added item to your watchlist!"
    
    ERROR = "Sorry, something went wrong. Please try again later."
    
    CANCELLED = "Tracking cancelled. You can start again with /track"

    @staticmethod
    def format_product_details(details: dict, link: str) -> str:
        return (
            f"<b>Product Name:</b> {details['product_name']}\n\n"
            f"<b>Current Price:</b> {details['currency']} {details['price']}\n\n"
            f"<b>Link:</b> <a href='{link}'>{link}</a>\n\n"
            "Now, please send your target price."
        )

    @staticmethod
    def format_confirmation(data: dict) -> str:
        return (
            f"<b>Product Name:</b> {data['product_name']}\n\n"
            f"<b>Current Price:</b> {data['currency']} {data['current_price']}\n\n"
            f"<b>Target Price:</b> {data['currency']} {data['target_price']}\n\n"
            f"<b>Link:</b> <a href='{data['product_link']}'>{data['product_link']}</a>\n\n"
            "Do you want to save this tracking item?"
        )

class TrackKeyboardFactory:
    @staticmethod
    def get_confirmation_keyboard() -> InlineKeyboardBuilder:
        kb = InlineKeyboardBuilder()
        kb.button(text="Confirm", callback_data="confirm")
        kb.button(text="Cancel", callback_data="cancel")
        return kb.as_markup()

@track_item_router.message(Command("cancel"))
async def cancel_command_handler(message: Message, state: FSMContext) -> None:
    """Handle the /cancel command."""
    if not message.from_user:
        logger.error("Received message without user information")
        await message.answer("Error: Could not identify user.")
        return

    user_id = message.from_user.id
    logger.info(f"Cancel command received from user {user_id}")

    await message.answer(TrackMessages.CANCELLED)
    await state.clear()

@track_item_router.message(Command("track"))
async def command_track_handler(message: Message, state: FSMContext) -> None:
    """Handle the /track command."""
    if not message.from_user:
        logger.error("Received message without user information")
        await message.answer("Error: Could not identify user.")
        return

    user_id = message.from_user.id
    logger.info(f"Track command received from user {user_id}")

    try:
        with get_db() as db:
            if not await tracked_item_service.check_tracking_limit(db, user_id):
                await message.answer(TrackMessages.LIMIT_REACHED)
                return

        await message.answer(TrackMessages.REQUEST_LINK)
        await state.set_state(TrackStates.product_link)
    except Exception as e:
        logger.error(f"Error in track command for user {user_id}: {str(e)}")
        await message.answer(TrackMessages.ERROR)

@track_item_router.message(TrackStates.product_link)
async def link_received_handler(message: Message, state: FSMContext) -> None:
    """Handle product link input."""
    if not message.text or not validators.url(message.text):
        await message.answer(TrackMessages.INVALID_URL)
        return

    user_id = message.from_user.id
    logger.info(f"Processing link from user {user_id}")

    try:
        processing_msg = await message.answer(TrackMessages.PROCESSING)
        product_details = await scraper.scrape(url=message.text)

        if not product_details or not product_details['is_trackable']:
            await processing_msg.edit_text(TrackMessages.CANNOT_TRACK)
            await state.clear()
            return

        await processing_msg.edit_text(TrackMessages.CAN_TRACK)
        print(product_details)

        await state.update_data(
            product_link=message.text,
            product_name=product_details["product_name"],
            current_price=product_details["price"],
            currency=product_details["currency"],
        )

        print("Here?")

        await message.answer(
            TrackMessages.format_product_details(product_details, message.text),
            parse_mode="HTML",
        )
        await state.set_state(TrackStates.target_price)

    except Exception as e:
        logger.error(f"Error processing link for user {user_id}: {str(e)}")
        await message.answer(TrackMessages.ERROR)
        await state.clear()

@track_item_router.message(TrackStates.target_price)
async def target_price_received_handler(message: Message, state: FSMContext) -> None:
    """Handle target price input."""
    try:
        price = int(message.text)
        if price <= 0:
            await message.answer(TrackMessages.PRICE_TOO_LOW)
            return
    except ValueError:
        await message.answer(TrackMessages.INVALID_PRICE)
        return

    await state.update_data(target_price=price)
    data = await state.get_data()
    
    await message.answer(
        TrackMessages.format_confirmation(data),
        parse_mode="HTML",
        reply_markup=TrackKeyboardFactory.get_confirmation_keyboard()
    )
    await state.set_state(TrackStates.confirmation)

@track_item_router.callback_query(TrackStates.confirmation, F.data == "confirm")
async def confirm_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle tracking confirmation."""
    await callback.answer()
    user_id = callback.from_user.id
    data = await state.get_data()

    try:
        await callback.message.edit_text(TrackMessages.ADDING_ITEM)
        
        with get_db() as db:
            tracked_item_service.repository.create(
                db,
                user_id=user_id,
                name=data["product_name"],
                link=data["product_link"],
                current_price=data["current_price"],
                target_price=data["target_price"],
                currency=data["currency"]
            )
            
        await callback.message.edit_text(TrackMessages.SUCCESS)
    except Exception as e:
        logger.error(f"Error confirming track for user {user_id}: {str(e)}")
        await callback.message.edit_text(TrackMessages.ERROR)
    finally:
        await state.clear()

@track_item_router.callback_query(TrackStates.confirmation, F.data == "cancel")
async def cancel_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle tracking cancellation."""
    await callback.answer()
    await callback.message.edit_text(TrackMessages.CANCELLED)
    await state.clear()

@track_item_router.error()
async def error_handler(event: ErrorEvent) -> None:
    """Handle errors in the track flow."""
    logger.error(f"Error in track handler: {event.exception}", exc_info=True)
    
    try:
        if event.update.message:
            await event.update.message.answer(TrackMessages.ERROR)
        elif event.update.callback_query:
            await event.update.callback_query.message.edit_text(TrackMessages.ERROR)
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

