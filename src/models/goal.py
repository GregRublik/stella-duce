from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from db.database import Base


class GoalStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    title = Column(String(500), nullable=False)
    description = Column(Text)

    status = Column(
        Enum(GoalStatus, name="goal_status"),
        default=GoalStatus.DRAFT,
        nullable=False
    )

    priority = Column(Integer, default=1)
    target_date = Column(DateTime)
    completed_at = Column(DateTime)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    # Связь со стадиями
    stages = relationship(
        "GoalStage",
        back_populates="goal",
        cascade="all, delete-orphan",
        order_by="GoalStage.order_index"
    )

    def __repr__(self):
        return f"<Goal(id={self.id}, title='{self.title[:30]}')>"