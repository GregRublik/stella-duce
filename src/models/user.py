from datetime import datetime, timezone

from sqlalchemy import Column, Integer, Boolean, DateTime, String, LargeBinary, ForeignKey, UUID
from sqlalchemy_utils import EmailType
from sqlalchemy.sql import func
from db.database import Base
import uuid
import time

from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(EmailType, unique=True, nullable=False)
    password = Column(LargeBinary, nullable=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    # stage_progress = relationship("UserStageProgress", back_populates="user", cascade="all, delete-orphan")

class TokenUser(Base):
    __tablename__ = 'tokens_users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    token_hash = Column(LargeBinary, nullable=False, unique=True, index=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    rotated_at = Column(DateTime(timezone=True), nullable=True)

    expires_at = Column(DateTime(timezone=True), nullable=False)

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at
