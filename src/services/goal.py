from typing import List, Union

from repositories.base import SQLAlchemyRepository
from repositories.goal import GoalRepository
from exceptions import ModelNoFoundException, GoalNoFoundException
from schemas.goal import GoalResponse, CreateGoal, CreateGoalDB, UpdateGoal
from services.unit_of_work import UnitOfWork


class GoalService:

    def __init__(self, repository: Union[SQLAlchemyRepository, GoalRepository], uow: UnitOfWork):
        self.repository = repository
        self.uow = uow

    async def add_goal(self, user_id: int, goal: CreateGoal) -> GoalResponse:
        goal_db = CreateGoalDB(**goal.model_dump(), user_id=user_id)
        async with self.uow:
            return await self.repository.add_one(self.uow.session, goal_db.model_dump())

    async def get_goal(self, user_id, goal_id: int) -> GoalResponse:
        goal_db = await self.repository.get_by_id(self.uow.session, goal_id)
        if goal_db.user_id == user_id:
            return await self.repository.get_by_id(self.uow.session, goal_id)
        raise GoalNoFoundException

    async def delete_one(self, user_id, goal_id: int) -> GoalResponse:

        try:
            goal_db = await self.get_goal(user_id, goal_id)
            if goal_db.user_id == user_id:
                async with self.uow:
                    return await self.repository.delete_by_id(self.uow.session, goal_id)
            raise GoalNoFoundException
        except ModelNoFoundException:
            raise GoalNoFoundException

    async def change_goal(self, user_id: int, goal_id: int, goal: UpdateGoal) -> GoalResponse | None:
        try:
            goal_db = await self.get_goal(user_id, goal_id)
            if goal_db.user_id == user_id:
                async with self.uow:
                    return await self.repository.change_one(self.uow.session, goal_id, goal.model_dump(exclude_unset=True))
            raise GoalNoFoundException
        except ModelNoFoundException:
            raise GoalNoFoundException

    async def get_goals(self, user_id) -> List[GoalResponse]:
        try:
            return await self.repository.get_by_user_id(self.uow.session, user_id)
        except ModelNoFoundException:
            raise