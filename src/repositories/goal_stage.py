from models.goal_stage import GoalStage
from repositories.base import SQLAlchemyRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class GoalStageRepository(SQLAlchemyRepository):
    model = GoalStage

    async def get_by_goal_id(self, session: AsyncSession, goal_id: int):
        stmt = select(self.model).where(self.model.goal_id == goal_id)

        res = await session.execute(stmt)
        return res.scalars().all()

    async def get_by_ids(self, session: AsyncSession, ids: list[int]):
        if not ids:
            return []

        stmt = select(self.model).where(self.model.id.in_(ids))

        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_ids_and_goal(
            self,
            session: AsyncSession,
            ids: list[int],
            goal_id: int
    ):
        stmt = (
            select(self.model)
            .where(
                self.model.id.in_(ids),
                self.model.goal_id == goal_id
            )
        )

        result = await session.execute(stmt)
        return result.scalars().all()
