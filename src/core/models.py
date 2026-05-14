"""
This module defines the database models and schemas, including the Task model.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy declarative models.
    """

class Task(Base):
    """
    Database model representing an ad generation task.
    """
    __tablename__ = 'tasks'

    # Core fields with auto-generated UUID
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    status: Mapped[str] = mapped_column(String, default='processing')
    keyword: Mapped[str] = mapped_column(String)

    # JSONB field to store generated ad copies
    result: Mapped[dict] = mapped_column(JSONB, nullable=True)

    # Timestamps with timezone info
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda:datetime.now(timezone.utc))
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)