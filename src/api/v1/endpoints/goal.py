from fastapi import APIRouter, Depends, status
from dependencies.user import get_current_user_id
from depends import get_goal_service
from exceptions import GoalNoFoundException, APIException
from typing import Annotated

from schemas.response import APIResponse
from services.goal import GoalService
from response import ok, UnifiedResponseRoute

from schemas.goal import GoalResponse, CreateGoal, UpdateGoal

router = APIRouter(
    tags=["Goals"],
    route_class=UnifiedResponseRoute
)


@router.get("/goals", response_model=APIResponse[list[GoalResponse]])
async def get_goals(
        user_id: Annotated[int, Depends(get_current_user_id)],
        goal_service: Annotated[GoalService, Depends(get_goal_service)]
):
    goals = await goal_service.get_goals(user_id)
    return ok(goals)


@router.get("/goals/{goal_id}", response_model=APIResponse[GoalResponse])
async def get_goal(
        goal_id: int,
        user_id: Annotated[int, Depends(get_current_user_id)],
        goal_service: Annotated[GoalService, Depends(get_goal_service)]
):
    try:
        goal = await goal_service.get_goal(user_id, goal_id)
        return ok(goal)
    except GoalNoFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )


@router.post("/goals", response_model=APIResponse[GoalResponse], status_code=status.HTTP_201_CREATED)
async def create_goal(
        data_goal: CreateGoal,
        user_id: Annotated[int, Depends(get_current_user_id)],
        goal_service: Annotated[GoalService, Depends(get_goal_service)]
):
    goal = await goal_service.add_goal(user_id, data_goal)
    return ok(goal)

@router.patch("/goals/{goal_id}", response_model=APIResponse[GoalResponse])
async def update_goal(
        goal_id: int,
        data_goal: UpdateGoal,
        user_id: Annotated[int, Depends(get_current_user_id)],
        goal_service: Annotated[GoalService, Depends(get_goal_service)]
):
    try:
        goal = await goal_service.change_goal(user_id, goal_id, data_goal)
        return ok(goal)
    except GoalNoFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )

@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
        goal_id: int,
        user_id: Annotated[int, Depends(get_current_user_id)],
        goal_service: Annotated[GoalService, Depends(get_goal_service)]
):
    try:
        await goal_service.delete_one(user_id, goal_id)
    except GoalNoFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )
