from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

from models.goal_stage import StageStatus


class GoalStageResponse(BaseModel):
    id: int
    goal_id: int

    # Основная информация
    title: str
    description: Optional[str] = None
    detailed_instructions: Optional[str] = None

    # Статус
    status: StageStatus
    order_index: int
    is_milestone: bool

    # Даты
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None

    # Оценочные параметры
    estimated_duration_hours: Optional[float] = None
    difficulty_level: Optional[int] = Field(default=None, ge=1, le=5)

    # Зависимости (id стадий, от которых зависит текущая)
    dependency_ids: List[int] = []

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreateGoalStage(BaseModel):
    title: str = Field(..., max_length=500)

    description: Optional[str] = None
    detailed_instructions: Optional[str] = None

    order_index: Optional[int] = None
    is_milestone: bool = False

    estimated_duration_hours: Optional[float] = Field(default=None, ge=0)
    difficulty_level: Optional[int] = Field(default=None, ge=1, le=5)

    dependency_ids: Optional[List[int]] = None


class UpdateGoalStage(BaseModel):
    title: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = None
    detailed_instructions: Optional[str] = None

    status: Optional[StageStatus] = None
    order_index: Optional[int] = None
    is_milestone: Optional[bool] = None

    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None

    estimated_duration_hours: Optional[float] = Field(default=None, ge=0)
    difficulty_level: Optional[int] = Field(default=None, ge=1, le=5)

    dependency_ids: Optional[List[int]] = None
