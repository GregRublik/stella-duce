
from sqlalchemy import Column, Integer, Boolean, DateTime
from sqlalchemy.sql import func
from db.database import Base

from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    stage_progress = relationship("UserStageProgress", back_populates="user", cascade="all, delete-orphan")
