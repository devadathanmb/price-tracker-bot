import datetime
from sqlalchemy import BigInteger, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from db.base import Base

class TrackedItem(Base):
    """Model representing a tracked item in the price tracking system."""
    __tablename__ = "tracked_items"

    # Primary key and relationships
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )

    # Item details
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    target_price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    link: Mapped[str] = mapped_column(String, nullable=False)

    # Timestamps
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=datetime.datetime.now(datetime.timezone.utc)
    )
    last_checked_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=datetime.datetime.now(datetime.timezone.utc)
    )

    # Relationships
    user = relationship("User", back_populates="tracked_items", cascade="all, delete")


