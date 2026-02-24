from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import Base


class StageDependency(Base):
    __tablename__ = "stage_dependencies"

    id = Column(Integer, primary_key=True)

    prerequisite_stage_id = Column(
        Integer,
        ForeignKey("goal_stages.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    dependent_stage_id = Column(
        Integer,
        ForeignKey("goal_stages.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    prerequisite_stage = relationship(
        "GoalStage",
        foreign_keys=[prerequisite_stage_id],
        backref="dependent_relations"
    )

    dependent_stage = relationship(
        "GoalStage",
        foreign_keys=[dependent_stage_id],
        back_populates="dependencies"
    )

    __table_args__ = (
        UniqueConstraint(
            "prerequisite_stage_id",
            "dependent_stage_id",
            name="uq_stage_dependency"
        ),
        CheckConstraint(
            "prerequisite_stage_id != dependent_stage_id",
            name="no_self_dependency"
        ),
    )

    def __repr__(self):
        return (
            f"<StageDependency("
            f"{self.prerequisite_stage_id} -> {self.dependent_stage_id})>"
        )
