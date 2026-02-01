from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from models.goal import GoalStatus


class GoalResponse(BaseModel):
    # Порядок объявления полей определяет порядок в JSON
    id: int
    title: str
    description: str
    status: str
    priority: Optional[int] = None
    # user_id: int
    target_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Для работы с ORM моделями
    model_config = ConfigDict(from_attributes=True)

class CreateGoal(BaseModel):
    title: str
    description: Optional[str] = None

class CreateGoalDB(CreateGoal):
    status: GoalStatus = GoalStatus.DRAFT
    user_id: int

class UpdateGoal(CreateGoal):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[GoalStatus] = None
    target_date: Optional[datetime] = None
    priority: Optional[int] = None

class DeleteGoal(BaseModel):
    id: int
