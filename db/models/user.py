from sqlalchemy import Column, BigInteger
from sqlalchemy.orm import relationship
from db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    tracked_items = relationship("TrackedItem", back_populates="user", cascade="all, delete-orphan")

