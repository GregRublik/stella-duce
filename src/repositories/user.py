from repositories.base import SQLAlchemyRepository
from models.user import User
from schemas.auth import UserEmail
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from exceptions import UserNoFoundException

class UserRepository(SQLAlchemyRepository):
    model = User

    async def get_by_email(self, session: AsyncSession, user: UserEmail) -> User:
        stmt = (
            select(self.model)
            .where(self.model.email == user.email)
            .limit(1)
        )
        try:
            res = await session.execute(stmt)
            return res.scalar_one()
        except NoResultFound:
            raise UserNoFoundException
