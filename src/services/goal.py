from sqlalchemy.ext.asyncio import AsyncSession

from models.goal import Goal
from repositories.base import SQLAlchemyRepository

from typing import Union, List

from repositories.goal import GoalRepository
from exceptions import ModelNoFoundException
from schemas.goal import GoalResponse


class GoalService:

    def __init__(self, repository: Union[SQLAlchemyRepository, GoalRepository], session: AsyncSession):
        self.repository = repository
        self.session = session

    async def get_goal(self, goal_id: int) -> Goal:
        return await self.repository.get_by_id(self.session, goal_id)

    async def get_goals_user(self, user_id) -> List[GoalResponse]:
        try:
            return [GoalResponse.model_validate(goal) for goal in await self.repository.get_by_user_id(self.session, user_id)]
        except ModelNoFoundException:
            raise