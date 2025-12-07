from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Float, Boolean, JSON, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from db.database import Base


class ProgressType(enum.Enum):
    """Типы обновления прогресса"""
    MANUAL = "manual"  # Ручное обновление пользователем
    AUTOMATIC = "automatic"  # Автоматическое (по времени/триггерам)
    AI_SUGGESTED = "ai_suggested"  # Предложено ИИ
    SYSTEM = "system"  # Системное (при завершении зависимости и т.д.)


class UserStageProgress(Base):
    __tablename__ = 'user_stage_progress'

    id = Column(Integer, primary_key=True, index=True)

    # Связи
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    stage_id = Column(Integer, ForeignKey('goal_stages.id', ondelete='CASCADE'), nullable=False, index=True)

    # Текущее состояние прогресса
    progress_percentage = Column(Integer, default=0, nullable=False)  # 0-100%
    previous_progress = Column(Integer, default=0)  # Предыдущее значение для отслеживания изменений

    # Статус и активность
    current_status = Column(Enum('not_started', 'in_progress', 'completed', 'paused', 'blocked'),
                            default='not_started', nullable=False)
    is_active = Column(Boolean, default=True)  # Активно ли отслеживание этого этапа

    # Временные метки работы над этапом
    started_at = Column(DateTime)  # Когда пользователь начал этап
    last_worked_on = Column(DateTime)  # Последний раз работал над этапом
    completed_at = Column(DateTime)  # Когда завершил этап

    # Метрики времени
    total_time_spent_minutes = Column(Float, default=0.0)  # Общее затраченное время в минутах
    estimated_remaining_minutes = Column(Float)  # Оставшееся время по оценке

    # Оценки сложности и удовлетворения
    user_difficulty_rating = Column(Integer)  # Оценка сложности от пользователя (1-5)
    user_satisfaction_rating = Column(Integer)  # Удовлетворенность выполнением (1-5)

    # Детали выполнения
    notes = Column(Text)  # Заметки пользователя по этапу
    resources_used = Column(JSON)  # Список использованных ресурсов
    blockers = Column(Text)  # Что мешает выполнению

    # Метрики качества
    quality_score = Column(Integer)  # Оценка качества выполнения (0-100)
    revision_count = Column(Integer, default=0)  # Сколько раз переделывали/пересматривали

    # Тип и источник обновления
    last_update_type = Column(Enum(ProgressType), default=ProgressType.MANUAL)
    ai_feedback = Column(Text)  # Обратная связь от ИИ по прогрессу

    # Технические поля
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Связи
    user = relationship("User", back_populates="stage_progress")
    stage = relationship("GoalStage", back_populates="progress_records")

    __table_args__ = (
        # Правильный синтаксис для UniqueConstraint
        UniqueConstraint('user_id', 'stage_id'),
    )

    def __repr__(self):
        return f"<UserStageProgress(user={self.user_id}, stage={self.stage_id}, progress={self.progress_percentage}%)>"
