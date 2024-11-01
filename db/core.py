from contextlib import contextmanager
from typing import Generator
from config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from utils.logger import get_logger

logger = get_logger(__name__)

class Database:
    def __init__(self, database_url: str):
        self._db_url = database_url
        self._engine = None
        self._session_factory = None
        self._init_engine()

    def _init_engine(self) -> None:
        logger.info("Initializing database engine...")
        self._engine = create_engine(
            self._db_url,
            pool_size=20,
            max_overflow=10,
            pool_timeout=30,
            pool_pre_ping=True
        )
        
        self._session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine
        )
        logger.info("Database engine initialized successfully")

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        session: Session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Transaction rolled back due to: {str(e)}")
            raise
        finally:
            session.close()

db = Database(database_url=Config.DB_SERVICE_URI)
get_db = db.get_session
