from fastapi import APIRouter, Depends, status
from typing import Annotated

from dependencies.user import get_current_user_id
from depends import get_goal_stage_service
from exceptions import (
    GoalStageNoFoundException,
    APIException,
    GoalStageAlreadyExistsException,
    InvalidStageDependencyException,
    GoalNoFoundException,
    ForbiddenException
)
from schemas.response import APIResponse
from services.goal_stage import GoalStageService
from response import ok, UnifiedResponseRoute

from schemas.goal_stage import GoalStageResponse, CreateGoalStage, UpdateGoalStage

router = APIRouter(
    tags=["Goal Stages"],
    route_class=UnifiedResponseRoute
)


@router.get("/goals/{goal_id}/stages", response_model=APIResponse[list[GoalStageResponse]])
async def get_goal_stages(
        goal_id: int,
        user_id: Annotated[int, Depends(get_current_user_id)],
        stage_service: Annotated[GoalStageService, Depends(get_goal_stage_service)]
):
    try:
        stages = await stage_service.get_stages(user_id, goal_id)
        return ok(stages)
    except (GoalNoFoundException, GoalStageNoFoundException) as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )
    except ForbiddenException as e:
        raise APIException(
            status_code=status.HTTP_403_FORBIDDEN,
            error=e.detail
        )


@router.get("/goals/{goal_id}/stages/{stage_id}", response_model=APIResponse[GoalStageResponse])
async def get_goal_stage(
        goal_id: int,
        stage_id: int,
        user_id: Annotated[int, Depends(get_current_user_id)],
        stage_service: Annotated[GoalStageService, Depends(get_goal_stage_service)]
):
    try:
        stage = await stage_service.get_stage(user_id, goal_id, stage_id)
        return ok(stage)
    except GoalStageNoFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )
    except ForbiddenException as e:
        raise APIException(
            status_code=status.HTTP_403_FORBIDDEN,
            error=e.detail
        )


@router.post("/goals/{goal_id}/stages", response_model=APIResponse[GoalStageResponse], status_code=status.HTTP_201_CREATED)
async def create_goal_stage(
        goal_id: int,
        stage_data: CreateGoalStage,
        user_id: Annotated[int, Depends(get_current_user_id)],
        stage_service: Annotated[GoalStageService, Depends(get_goal_stage_service)]
):
    try:
        stage = await stage_service.add_stage(user_id, goal_id, stage_data)
        return ok(stage)
    except GoalStageAlreadyExistsException as e:
        raise APIException(
            status_code=status.HTTP_409_CONFLICT,
            error=e.detail
        )
    except InvalidStageDependencyException as e:
        raise APIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error=e.detail
        )
    except ForbiddenException as e:
        raise APIException(
            status_code=status.HTTP_403_FORBIDDEN,
            error=e.detail
        )

@router.patch("/goals/{goal_id}/stages/{stage_id}", response_model=APIResponse[GoalStageResponse])
async def update_goal_stage(
        goal_id: int,
        stage_id: int,
        data_goal: UpdateGoalStage,
        user_id: Annotated[int, Depends(get_current_user_id)],
        stage_service: Annotated[GoalStageService, Depends(get_goal_stage_service)]
):
    try:
        stage = await stage_service.change_stage(user_id, goal_id, stage_id, data_goal)
        return ok(stage)
    except GoalStageNoFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )

@router.delete("/goals/{goal_id}/stages/{stage_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal_stage(
        goal_id: int,
        stage_id: int,
        user_id: Annotated[int, Depends(get_current_user_id)],
        stage_service: Annotated[GoalStageService, Depends(get_goal_stage_service)]
):
    try:
        await stage_service.delete_one(user_id, goal_id, stage_id)
    except (GoalNoFoundException, GoalStageNoFoundException) as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )
    except ForbiddenException as e:
        raise APIException(
            status_code=status.HTTP_403_FORBIDDEN,
            error=e.detail
        )
