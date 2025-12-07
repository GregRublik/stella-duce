from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Float, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from db.database import Base


class StageStatus(enum.Enum):
    """Статусы этапа"""
    NOT_STARTED = "not_started"  # Ещё не начат
    IN_PROGRESS = "in_progress"  # В процессе выполнения
    COMPLETED = "completed"  # Завершён
    BLOCKED = "blocked"  # Заблокирован (зависит от других этапов)
    SKIPPED = "skipped"  # Пропущен


class GoalStage(Base):
    __tablename__ = 'goal_stages'

    id = Column(Integer, primary_key=True, index=True)

    # Связь с целью
    goal_id = Column(Integer, ForeignKey('goals.id', ondelete='CASCADE'), nullable=False, index=True)
    goal = relationship("Goal", back_populates="stages")

    # Основная информация
    title = Column(String(500), nullable=False)
    description = Column(Text)
    detailed_instructions = Column(Text)  # Подробные инструкции от ИИ

    # Статус и прогресс
    status = Column(Enum(StageStatus), default=StageStatus.NOT_STARTED, nullable=False)
    progress_percentage = Column(Integer, default=0)  # 0-100%
    is_milestone = Column(Boolean, default=False)  # Является ли ключевой вехой
    order_index = Column(Integer, default=0)  # Порядковый номер в roadmap

    # Даты
    estimated_start_date = Column(DateTime)
    estimated_end_date = Column(DateTime)
    actual_start_date = Column(DateTime)
    actual_end_date = Column(DateTime)

    # Сложность и время
    estimated_duration_hours = Column(Float)  # Оценка в часах
    difficulty_level = Column(Integer)  # Уровень сложности 1-5
    ai_confidence = Column(Integer)  # Уверенность ИИ в этом этапе (0-100)

    # Позиционирование в roadmap (для визуализации)
    position_x = Column(Float, default=0.0)  # X координата на карте
    position_y = Column(Float, default=0.0)  # Y координата на карте

    # Метаданные и теги
    tags = Column(JSON)  # Список тегов ["theory", "практика", "сложный"]
    prerequisites = Column(JSON)  # ID этапов-предпосылок [2, 5, 8]

    # Связи с другими таблицами
    dependencies = relationship(
        "StageDependency",
        foreign_keys="[StageDependency.dependent_stage_id]",
        back_populates="dependent_stage",
        cascade="all, delete-orphan"
    )
    progress_records = relationship("UserStageProgress", back_populates="stage", cascade="all, delete-orphan")
    calendar_events = relationship("CalendarEvent", back_populates="stage", cascade="all, delete-orphan")
    history = relationship("StageHistory", back_populates="stage", cascade="all, delete-orphan")

    # Технические поля
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<GoalStage(id={self.id}, title='{self.title[:30]}...', status='{self.status}')>"