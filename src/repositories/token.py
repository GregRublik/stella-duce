from repositories.base import SQLAlchemyRepository
from models.user import TokenUser
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from exceptions import TokenUserNoFoundException
from schemas.token import TokenUserUpdate

class TokenUserRepository(SQLAlchemyRepository):
    model = TokenUser

    async def get_by_user_id(self, session: AsyncSession, user_id) -> TokenUser:
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .limit(1)
        )
        try:
            res = await session.execute(stmt)
            return res.scalar_one()
        except NoResultFound:
            raise TokenUserNoFoundException

    async def update_by_id(self, session: AsyncSession, updated_token: TokenUserUpdate) -> TokenUser:
        stmt = (
            update(self.model)
            .where(self.model.id == updated_token.id)
        )
        try:
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()
        except NoResultFound:
            raise TokenUserNoFoundException
