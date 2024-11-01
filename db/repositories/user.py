from collections.abc import Sequence
from typing import List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.models.user import User
from utils.logger import get_logger

logger = get_logger(__name__)

class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        try:
            stmt = select(User).where(User.id == user_id)
            return db.scalar(stmt)
        except Exception as e:
            logger.error(f"Error retrieving user {user_id}: {str(e)}")
            raise

    @staticmethod
    def get_all(db: Session) -> Sequence[User]:
        try:
            stmt = select(User)
            return db.scalars(stmt).all()
        except Exception as e:
            logger.error(f"Error retrieving all users : {str(e)}")
            raise

    @staticmethod
    def create(db: Session, user_id: int) -> User:
        try:
            user = User(id=user_id)
            db.add(user)
            logger.info(f"Created user {user_id}")
            return user
        except Exception as e:
            logger.error(f"Error creating user {user_id}: {str(e)}")
            raise

    @staticmethod
    def get_or_create(db: Session, user_id: int) -> Tuple[User, bool]:
        try:
            user = UserRepository.get_by_id(db, user_id)
            if user:
                return user, False
            user = UserRepository.create(db, user_id)
            return user, True
        except Exception as e:
            logger.error(f"Error in get_or_create for user {user_id}: {str(e)}")
            raise

class UserService:
    def __init__(self):
        self.repository = UserRepository()

    async def ensure_user_exists(self, db: Session, user_id: int) -> User:
        try:
            user, _ = self.repository.get_or_create(db, user_id)
            return user
        except Exception as e:
            logger.error(f"Error ensuring user exists {user_id}: {str(e)}")
            raise

user_service = UserService()
