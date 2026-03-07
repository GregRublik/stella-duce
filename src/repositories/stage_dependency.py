from typing import List, Dict
from sqlalchemy import insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.base import SQLAlchemyRepository
from models.stage_dependency import StageDependency


class StageDependencyRepository(SQLAlchemyRepository):
    model = StageDependency

    async def add_many(self, session: AsyncSession, data: List[Dict]):
        """Добавить несколько зависимостей"""
        stmt = (
            insert(self.model)
            .values(data)
            .returning(self.model)
        )

        await session.execute(stmt)

    async def delete_by_dependent(self, session: AsyncSession, stage_id: int
    ):
        stmt = delete(self.model).where(
            self.model.dependent_stage_id == stage_id
        )
        await session.execute(stmt)
