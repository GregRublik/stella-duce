from typing import List
from repositories.goal_stage import GoalStageRepository
from repositories.goal import GoalRepository

from models.goal_stage import StageStatus, GoalStage
from repositories.stage_dependency import StageDependencyRepository

from services.unit_of_work import UnitOfWork
from exceptions import (
    GoalStageNoFoundException,
    ModelAlreadyExistsException,
    GoalStageAlreadyExistsException,
    ModelNoFoundException,
    ForbiddenException,
    InvalidStageDependencyException
)

from schemas.goal_stage import GoalStageResponse, CreateGoalStage


class GoalStageService:

    def __init__(
        self,
        repository: GoalStageRepository,
        goal_repository: GoalRepository,
        stage_dependency_repository: StageDependencyRepository,
        uow: UnitOfWork
    ):
        self.repository = repository
        self.goal_repository = goal_repository
        self.stage_dependency_repository = stage_dependency_repository
        self.uow = uow


    async def _check_goal_owner(self, user_id: int, goal_id: int):
        """Проверка что goal принадлежит пользователю"""
        goal = await self.goal_repository.get_by_id(self.uow.session, goal_id)

        if not goal:
            raise ModelNoFoundException

        if goal.user_id != user_id:
            raise ForbiddenException

    @staticmethod
    def is_stage_ready(stage: GoalStage) -> bool:
        return all(
            dep.prerequisite_stage.status == StageStatus.COMPLETED
            for dep in stage.dependencies
        )

    async def get_stages(self, user_id: int, goal_id: int) -> List[GoalStageResponse]:
        try:
            await self._check_goal_owner(user_id, goal_id)

            return await self.repository.get_by_goal_id(self.uow.session, goal_id)

        except ModelNoFoundException:
            raise GoalStageNoFoundException

    async def add_stage(self, user_id: int, goal_id: int, data_stage: CreateGoalStage) -> GoalStage:
        try:
            async with self.uow:

                data_dict = data_stage.model_dump(exclude_unset=True)
                dependency_ids = data_dict.pop("dependency_ids", [])
                data_dict["goal_id"] = goal_id
                stage = await self.repository.add_one(self.uow.session, data_dict)

                # проверяем существование стадий
                if dependency_ids:

                    stages = await self.repository.get_by_ids(
                        self.uow.session,
                        dependency_ids
                    )

                    found_ids = {s.id for s in stages}

                    missing = set(dependency_ids) - found_ids

                    if missing:
                        raise InvalidStageDependencyException

                    deps = [
                        {
                            "prerequisite_stage_id": dep_id,
                            "dependent_stage_id": stage.id
                        }
                        for dep_id in dependency_ids
                    ]

                    await self.stage_dependency_repository.add_many(
                        self.uow.session,
                        deps
                    )
                return stage

        except ModelAlreadyExistsException:
            raise GoalStageAlreadyExistsException

