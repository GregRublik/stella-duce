from typing import List

from models.goal import Goal
from repositories.base import SQLAlchemyRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from exceptions import ModelNoFoundException, GoalNoFoundException


class GoalRepository(SQLAlchemyRepository):
    model = Goal

    async def get_by_user_id(self, session: AsyncSession, user_id: int):
        try:
            stmt = select(self.model).where(self.model.user_id == user_id)

            res = await session.execute(stmt)
            return [goal for goal in res.scalars().all()]
        except NoResultFound:
            raise ModelNoFoundException
