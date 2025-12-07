from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from db.database import Base


class DependencyType(enum.Enum):
    """Типы зависимостей между этапами"""
    FINISH_TO_START = "finish_to_start"  # Этап B начинается после завершения A
    START_TO_START = "start_to_start"  # Этап B начинается одновременно с A
    FINISH_TO_FINISH = "finish_to_finish"  # Этап B завершается одновременно с A
    START_TO_FINISH = "start_to_finish"  # Этап B завершается после начала A


class DependencyStrength(enum.Enum):
    """Сила/важность зависимости"""
    REQUIRED = "required"  # Обязательная зависимость
    RECOMMENDED = "recommended"  # Рекомендуемая зависимость
    OPTIONAL = "optional"  # Опциональная зависимость


class StageDependency(Base):
    __tablename__ = 'stage_dependencies'

    id = Column(Integer, primary_key=True, index=True)

    # Связи с этапами
    prerequisite_stage_id = Column(
        Integer,
        ForeignKey('goal_stages.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    dependent_stage_id = Column(
        Integer,
        ForeignKey('goal_stages.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Типы и свойства зависимостей
    dependency_type = Column(Enum(DependencyType), default=DependencyType.FINISH_TO_START, nullable=False)
    strength = Column(Enum(DependencyStrength), default=DependencyStrength.REQUIRED, nullable=False)

    # Логические флаги
    is_active = Column(Boolean, default=True)  # Активна ли зависимость
    is_satisfied = Column(Boolean, default=False)  # Выполнено ли условие зависимости

    # Детали зависимости
    lag_days = Column(Integer, default=0)  # Задержка в днях между этапами
    description = Column(Text)  # Описание почему эта зависимость существует

    # Технические поля
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Связи с объектами этапов
    prerequisite_stage = relationship(
        "GoalStage",
        foreign_keys=[prerequisite_stage_id],
        backref="dependent_relations"  # Обратная ссылка для предшествующего этапа
    )
    dependent_stage = relationship(
        "GoalStage",
        foreign_keys=[dependent_stage_id],
        back_populates="dependencies"  # Двусторонняя связь
    )

    # Ограничение уникальности, чтобы избежать дублирования зависимостей
    __table_args__ = (
        # Правильный синтаксис для UniqueConstraint
        UniqueConstraint('prerequisite_stage_id', 'dependent_stage_id'),
    )

    def __repr__(self):
        return f"<StageDependency(id={self.id}, prerequisite={self.prerequisite_stage_id} -> dependent={self.dependent_stage_id}, type={self.dependency_type})>"
