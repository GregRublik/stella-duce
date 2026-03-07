from typing import List, Dict
from sqlalchemy import insert
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
