from sqlalchemy import (
    Column, Integer, String, DateTime, Text,
    ForeignKey, Enum, Float, Boolean, Index
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from db.database import Base


class StageStatus(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class GoalStage(Base):
    __tablename__ = "goal_stages"

    id = Column(Integer, primary_key=True)

    goal_id = Column(
        Integer,
        ForeignKey("goals.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    goal = relationship("Goal", back_populates="stages")

    # Основная информация
    title = Column(String(500), nullable=False)
    description = Column(Text)
    detailed_instructions = Column(Text)

    # Статус
    status = Column(
        Enum(StageStatus, name="stage_status"),
        default=StageStatus.NOT_STARTED,
        nullable=False
    )

    order_index = Column(Integer, default=0, nullable=False)
    is_milestone = Column(Boolean, default=False)

    # Даты выполнения
    actual_start_date = Column(DateTime)
    actual_end_date = Column(DateTime)

    # Оценочные параметры
    estimated_duration_hours = Column(Float)
    difficulty_level = Column(Integer)  # 1–5

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    # Зависимости
    dependencies = relationship(
        "StageDependency",
        foreign_keys="StageDependency.dependent_stage_id",
        back_populates="dependent_stage",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_goal_order", "goal_id", "order_index"),
    )

    def __repr__(self):
        return f"<GoalStage(id={self.id}, title='{self.title[:30]}')>"
