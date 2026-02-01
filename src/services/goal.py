from sqlalchemy.ext.asyncio import AsyncSession

from models.goal import Goal, GoalStatus
from repositories.base import SQLAlchemyRepository

from typing import Union, List

from repositories.goal import GoalRepository
from exceptions import ModelNoFoundException, GoalNoFoundException
from schemas.goal import GoalResponse, CreateGoal, CreateGoalDB, UpdateGoal, DeleteGoal


class GoalService:

    def __init__(self, repository: Union[SQLAlchemyRepository, GoalRepository], session: AsyncSession):
        self.repository = repository
        self.session = session

    async def add_goal(self, user_id: int, goal: CreateGoal) -> GoalResponse:
        goal_db = CreateGoalDB(**goal.model_dump(), user_id=user_id)
        return await self.repository.add_one(self.session, goal_db.model_dump())

    async def get_goal(self, goal_id: int) -> GoalResponse:
        return await self.repository.get_by_id(self.session, goal_id)

    async def delete_one(self, user_id, goal: DeleteGoal) -> GoalResponse:

        try:
            goal_db = await self.get_goal(goal.id)
            if goal_db.user_id == user_id:
                return await self.repository.delete_by_id(self.session, goal.id)
            raise GoalNoFoundException
        except ModelNoFoundException:
            raise GoalNoFoundException

    async def change_goal(self,user_id: int, goal: UpdateGoal) -> GoalResponse | None:
        try:
            goal_db = await self.get_goal(goal.id)
            if goal_db.user_id == user_id:
                return await self.repository.change_one(self.session, goal.id, goal.model_dump())
            raise GoalNoFoundException
        except ModelNoFoundException:
            raise GoalNoFoundException

    async def get_goals_user(self, user_id) -> List[GoalResponse]:
        try:
            return await self.repository.get_by_user_id(self.session, user_id)
        except ModelNoFoundException:
            raise