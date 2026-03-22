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
    InvalidStageDependencyException,
    GoalNoFoundException
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
            raise GoalNoFoundException

        if goal.user_id != user_id:
            raise ForbiddenException

    @staticmethod
    def _build_graph(deps):
        graph = {}

        for prereq, dep in deps:
            graph.setdefault(prereq, []).append(dep)

        return graph

    @staticmethod
    def _creates_cycle(
            graph: dict[int, list[int]],
            start: int,
            target: int
    ) -> bool:
        """
        Проверка: появится ли цикл если добавить start -> target
        """

        visited = set()

        def dfs(node: int):
            if node == start:
                return True

            if node in visited:
                return False

            visited.add(node)

            for nxt in graph.get(node, []):
                if dfs(nxt):
                    return True

            return False

        return dfs(target)

    @staticmethod
    def is_stage_ready(stage: GoalStage) -> bool:
        return all(
            dep.prerequisite_stage.status == StageStatus.COMPLETED
            for dep in stage.dependencies
        )

    async def get_stages(self, user_id: int, goal_id: int) -> List[GoalStageResponse]:
        try:
            async with self.uow:
                await self._check_goal_owner(user_id, goal_id)
                return await self.repository.get_by_goal_id(self.uow.session, goal_id)

        except GoalNoFoundException:
            raise
        except ModelNoFoundException:
            raise GoalStageNoFoundException

    async def get_stage(self, user_id: int, goal_id: int, stage_id: int) -> GoalStageResponse:
        try:
            async with self.uow:
                await self._check_goal_owner(user_id, goal_id)
                stage = await self.repository.get_by_id(self.uow.session, stage_id)
            if stage.goal_id != goal_id:
                raise GoalStageNoFoundException
            return stage
        except ModelNoFoundException:
            raise GoalStageNoFoundException

    async def delete_one(self, user_id: int, goal_id: int, stage_id: int):
        try:
            async with self.uow:
                await self._check_goal_owner(user_id, goal_id)
                await self.repository.delete_by_id(self.uow.session, stage_id)
        except ModelNoFoundException:
            raise GoalStageNoFoundException

    async def add_stage(self, user_id: int, goal_id: int, stage_data: CreateGoalStage) -> GoalStage:

        try:
            async with self.uow:
                await self._check_goal_owner(user_id, goal_id)
                data_dict = stage_data.model_dump(exclude_unset=True)
                dependency_ids = data_dict.pop("dependency_ids", [])
                data_dict["goal_id"] = goal_id
                stage = await self.repository.add_one(self.uow.session, data_dict)

                # проверяем существование стадий
                if dependency_ids:

                    stages = await self.repository.get_by_ids_and_goal(
                        self.uow.session,
                        dependency_ids,
                        goal_id
                    )

                    found_ids = {s.id for s in stages}

                    missing = set(dependency_ids) - found_ids

                    if missing:
                        raise InvalidStageDependencyException

                    deps = await self.stage_dependency_repository.get_graph_by_goal(
                        self.uow.session,
                        goal_id
                    )

                    graph = self._build_graph(deps)

                    for dep_id in dependency_ids:

                        if self._creates_cycle(graph, dep_id, stage.id):
                            raise InvalidStageDependencyException

                    await self.stage_dependency_repository.add_many(
                        self.uow.session,
                        deps
                    )
                return stage

        except ModelAlreadyExistsException:
            raise GoalStageAlreadyExistsException

    async def change_stage(
            self,
            user_id: int,
            goal_id: int,
            stage_id: int,
            stage_data
    ) -> GoalStage:

        async with self.uow:

            await self._check_goal_owner(user_id, goal_id)

            data_dict = stage_data.model_dump(exclude_unset=True)
            dependency_ids = data_dict.pop("dependency_ids", None)

            stage = await self.repository.change_one(
                self.uow.session,
                stage_id,
                data_dict
            )

            if stage.goal_id != goal_id:
                raise GoalStageNoFoundException

            # если dependencies не переданы — не меняем их
            if dependency_ids is not None:

                stages = await self.repository.get_by_ids(
                    self.uow.session,
                    dependency_ids
                )

                found_ids = {s.id for s in stages}

                missing = set(dependency_ids) - found_ids

                if missing:
                    raise InvalidStageDependencyException

                # удаляем старые зависимости
                await self.stage_dependency_repository.delete_by_dependent(
                    self.uow.session,
                    stage_id
                )

                deps = [
                    {
                        "prerequisite_stage_id": dep_id,
                        "dependent_stage_id": stage_id
                    }
                    for dep_id in dependency_ids
                ]

                if deps:
                    await self.stage_dependency_repository.add_many(
                        self.uow.session,
                        deps
                    )

            return stage

