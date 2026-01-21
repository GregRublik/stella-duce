from sqlalchemy.ext.asyncio import AsyncSession

from typing import Union
from repositories.base import SQLAlchemyRepository
from repositories.user import UserRepository
# from schemas.users import UserCreate, UserLogin, User
from schemas.auth import UserLogin, UserCreate
from models.user import User
from exceptions import (
    UserAlreadyExistsException,
    ModelAlreadyExistsException,
    ModelNoFoundException,
    UserNoFoundException
)


class UserService:

    def __init__(self, repository: Union[SQLAlchemyRepository, UserRepository], session: AsyncSession):
        self.repository = repository
        self.session = session

    async def add_user(self, user: UserCreate) -> User:
        user_dict = user.model_dump()

        try:
            new_user = await self.repository.add_one(self.session, user_dict)
            return new_user
        except ModelAlreadyExistsException:
            raise UserAlreadyExistsException

    async def get_user(self, user: UserLogin) -> User:
        try:
            return await self.repository.get_by_email(self.session, user)
        except ModelNoFoundException:
            raise UserNoFoundException
