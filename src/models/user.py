from sqlalchemy import Column, Integer, Boolean, DateTime, String, LargeBinary, ForeignKey
from sqlalchemy_utils import EmailType
from sqlalchemy.sql import func
from db.database import Base
import uuid

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

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String, nullable=False, unique=True, index=True)  # Хэш токена
    is_active = Column(Boolean, default=True)

