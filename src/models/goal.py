from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from db.database import Base


class GoalStatus(enum.Enum):
    """Статусы цели"""
    DRAFT = "draft"  # Черновик (обсуждается с ИИ)
    PLANNING = "planning"  # Планирование (roadmap формируется)
    ACTIVE = "active"  # Активная цель
    PAUSED = "paused"  # Приостановлена
    COMPLETED = "completed"  # Завершена
    CANCELLED = "cancelled"  # Отменена


class Goal(Base):
    __tablename__ = 'goals'

    id = Column(Integer, primary_key=True, index=True)

    # Связь с пользователем
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user = relationship("User", back_populates="goals")

    # Основные поля
    title = Column(String(500), nullable=False)  # Название цели
    description = Column(Text)  # Подробное описание
    status = Column(Enum(GoalStatus), default=GoalStatus.DRAFT, nullable=False)
    priority = Column(Integer, default=1)  # Приоритет (1-10)

    # Даты
    target_date = Column(DateTime)  # Планируемая дата завершения
    completed_at = Column(DateTime)  # Фактическая дата завершения

    # # Метаданные ИИ
    # ai_model_used = Column(String(100))  # Какая модель ИИ использовалась
    # ai_summary = Column(Text)  # Краткое резюме от ИИ
    # ai_confidence = Column(Integer)  # Уверенность ИИ в плане (0-100)

    # Технические поля
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Связи с другими таблицами
    # stages = relationship("GoalStage", back_populates="goal", cascade="all, delete-orphan")
    # conversations = relationship("LLMConversation", back_populates="goal", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Goal(id={self.id}, title='{self.title[:30]}...', status='{self.status}')>"