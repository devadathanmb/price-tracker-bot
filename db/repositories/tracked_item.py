from typing import List
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from db.models.tracked_item import TrackedItem
from utils.logger import get_logger
from config import Config

logger = get_logger(__name__)

class TrackedItemRepository:
    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> List[TrackedItem]:
        try:
            stmt = select(TrackedItem).where(TrackedItem.user_id == user_id)
            return list(db.scalars(stmt))
        except Exception as e:
            logger.error(f"Error getting items for user {user_id}: {str(e)}")
            raise

    @staticmethod
    def create(db: Session, *, user_id: int, name: str, link: str,
               current_price: float, target_price: float, currency: str) -> TrackedItem:
        try:
            item = TrackedItem(
                user_id=user_id,
                name=name,
                link=link,
                current_price=current_price,
                target_price=target_price,
                currency=currency
            )
            db.add(item)
            return item
        except Exception as e:
            logger.error(f"Error creating item for user {user_id}: {str(e)}")
            raise

    @staticmethod
    def delete_by_id(db: Session, *, item_id: int, user_id: int) -> bool:
        try:
            stmt = delete(TrackedItem).where(
                TrackedItem.id == item_id,
                TrackedItem.user_id == user_id
            )
            result = db.execute(stmt)
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting item {item_id}: {str(e)}")
            raise

    @staticmethod
    def delete_all_by_user(db: Session, user_id: int) -> int:
        try:
            stmt = delete(TrackedItem).where(TrackedItem.user_id == user_id)
            result = db.execute(stmt)
            return result.rowcount
        except Exception as e:
            logger.error(f"Error deleting items for user {user_id}: {str(e)}")
            raise

class TrackedItemService:
    def __init__(self):
        self.repository = TrackedItemRepository()

    async def check_tracking_limit(self, db: Session, user_id: int) -> bool:
        items = self.repository.get_by_user_id(db, user_id)
        return len(items) < Config.MAX_ITEM_LIMIT

tracked_item_service = TrackedItemService()
