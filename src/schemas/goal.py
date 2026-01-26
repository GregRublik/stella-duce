from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class GoalResponse(BaseModel):
    # Порядок объявления полей определяет порядок в JSON
    id: int
    title: str
    description: str
    status: str
    priority: Optional[str] = None
    user_id: int
    target_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Для работы с ORM моделями
    model_config = ConfigDict(from_attributes=True)
