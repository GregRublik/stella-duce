from fastapi import APIRouter, Depends
from dependencies.user import get_current_user, get_current_user_id
from depends import get_goal_service
from models.user import User
from models.goal import Goal
from typing import Annotated
from services.goal import GoalService

from schemas.goal import GoalResponse


router = APIRouter(tags=["goals"])


@router.get("/goals", response_model=list[GoalResponse])
async def get_goals(
        user_id: Annotated[int, Depends(get_current_user_id)],
        goal_service: Annotated[GoalService, Depends(get_goal_service)]
):
    return await goal_service.get_goals_user(user_id)
