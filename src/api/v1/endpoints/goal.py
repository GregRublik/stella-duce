from fastapi import APIRouter, Depends, HTTPException, status
from dependencies.user import get_current_user, get_current_user_id
from depends import get_goal_service
from exceptions import GoalNoFoundException, ModelNoFoundException, APIException
from models.user import User
from models.goal import Goal
from typing import Annotated

from routes import UnifiedResponseRoute
from schemas.response import APIResponse
from services.goal import GoalService
from response import ok

from schemas.goal import GoalResponse, CreateGoal, UpdateGoal, DeleteGoal

router = APIRouter(
    tags=["goals"],
    route_class=UnifiedResponseRoute
)


@router.get("/goals", response_model=APIResponse[list[GoalResponse]])
async def get_goals(
        user_id: Annotated[int, Depends(get_current_user_id)],
        goal_service: Annotated[GoalService, Depends(get_goal_service)]
):
    goals = await goal_service.get_goals_user(user_id)
    return ok(goals)


@router.post("/goals", response_model=APIResponse[GoalResponse])
async def create_goal(
        data_goal: CreateGoal,
        user_id: Annotated[int, Depends(get_current_user_id)],
        goal_service: Annotated[GoalService, Depends(get_goal_service)]
):
    goal = await goal_service.add_goal(user_id, data_goal)
    return ok(goal)

@router.put("/goals/{goal_id}", response_model=APIResponse[GoalResponse])
async def update_goal(
        data_goal: UpdateGoal,
        user_id: Annotated[int, Depends(get_current_user_id)],
        goal_service: Annotated[GoalService, Depends(get_goal_service)]
):
    try:
        goal = await goal_service.change_goal(user_id, data_goal)
        return ok(goal)
    except GoalNoFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )

@router.delete("/goals/{goal_id}", response_model=APIResponse[GoalResponse])
async def delete_goal(
        data_goal: DeleteGoal,
        user_id: Annotated[int, Depends(get_current_user_id)],
        goal_service: Annotated[GoalService, Depends(get_goal_service)]
):
    try:
        goal = await goal_service.delete_one(user_id, data_goal)
        return ok(goal)
    except GoalNoFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )
