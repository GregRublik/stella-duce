from typing import Union, Annotated

from repositories.base import SQLAlchemyRepository
from repositories.user import UserRepository
from services.unit_of_work import UnitOfWork
from schemas.auth import UserCreate, UserEmail
from models.user import User, UserStatus
from exceptions import (
    UserAlreadyExistsException,
    ModelAlreadyExistsException,
    ModelNoFoundException,
    UserNoFoundException
)


class UserService:

    def __init__(self, repository: UserRepository, uow: UnitOfWork):
        self.repository = repository
        self.uow = uow

    async def add_user(self, user: UserCreate) -> User:
        user_dict = user.model_dump()

        try:
            async with self.uow:
                return await self.repository.add_one(self.uow.session, user_dict)
        except ModelAlreadyExistsException:
            raise UserAlreadyExistsException

    async def get_user_by_email(self, user: UserEmail) -> User:
        try:
            return await self.repository.get_by_email(self.uow.session, user)
        except ModelNoFoundException:
            raise UserNoFoundException

    async def get_user_by_id(self, user_id: int) -> User:
        try:
            return await self.repository.get_by_id(self.uow.session, user_id)
        except ModelNoFoundException:
            raise UserNoFoundException

    async def change_status_user(self, user_id: int, status: UserStatus) -> User:
        try:
            return await self.repository.change_one(self.uow.session, user_id, {"status": status})
        except ModelNoFoundException:
            raise UserNoFoundException
