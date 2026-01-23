import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal, Dict, Any, Optional, Union
import jwt
from pydantic import UUID4
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from constance import constants
from models.user import User, TokenUser
import bcrypt
from schemas.token import TokenUserCreate, TokenUserUpdate

from repositories.base import SQLAlchemyRepository
from repositories.token import TokenUserRepository
from exceptions import (
    TokenUserAlreadyExistsException,
    ModelAlreadyExistsException,
    TokenUserNoFoundException,
    ModelNoFoundException
)


class AuthService:

    def __init__(self, repository: Union[SQLAlchemyRepository, TokenUserRepository], session: AsyncSession):
        self.repository = repository
        self.session = session

    @staticmethod
    def decode_jwt(
            token: str,
            public_key: str = settings.jwt.public_key_path.read_text(),
            algorithm: str = settings.jwt.algorithm,
    ) -> dict:
        decoded = jwt.decode(
            token,
            public_key,
            algorithms=[algorithm],
        )
        return decoded

    @staticmethod
    def encode_jwt(
            payload: Dict[str, Any],
            expire_minutes: int,
            private_key: str,
            algorithm: str = constants.auth.ALGORITHM,
            expire_timedelta: Optional[timedelta] = None,
    ) -> str:

        to_encode = payload.copy()
        now = datetime.now(timezone.utc)

        expire = (
            now + expire_timedelta
            if expire_timedelta
            else now + timedelta(minutes=expire_minutes)
        )

        to_encode.update(
            exp=expire,
            iat=now,
        )

        encoded = jwt.encode(
            to_encode,
            private_key,
            algorithm=algorithm,
        )

        return encoded


    async def create_token(self, user: User, type_token: Literal['access', 'refresh']) -> str:

        types = {'access': constants.auth.EXPIRE_ACCESS_TOKEN, 'refresh': constants.auth.EXPIRE_REFRESH_TOKEN}

        token_id = uuid.uuid4()

        token = self.encode_jwt(
            {
                'sub': user.id,
                'jti': token_id,
            },
            types[type_token],
            private_key=settings.auth.private_key.read_text(),
        )

        if type_token == 'refresh':
            hashed_token = self.hashing(token)
            token_data = TokenUserCreate(id=token_id, user_id=user.id, token_hash=hashed_token).model_dump()
            await self.repository.add_one(self.session, token_data)
        return token

    @staticmethod
    def hashing(
            hashing_string: str,
    ) -> bytes:
        salt = bcrypt.gensalt()
        pwd_bytes: bytes = hashing_string.encode()
        return bcrypt.hashpw(pwd_bytes, salt)

    async def validate_refresh_token(self, token: str, user_id: int) -> bool:
        try:

            token_db = await self.repository.get_by_user_id(self.session, user_id)
            if token_db.token_hash == self.hashing(token):
                return True
            return False

        except TokenUserNoFoundException:
            return False

    async def add_token_user(self, token: TokenUserCreate) -> TokenUser:
        try:
            return await self.repository.add_one(self.session, token.model_dump())
        except ModelAlreadyExistsException:
            raise TokenUserAlreadyExistsException


    async def update_by_id(self, token: TokenUserUpdate) -> TokenUser:
        try:
            return await self.repository.update_by_id(self.session, token)
        except NoResultFound:
            raise TokenUserNoFoundException

    async def deactivate_token_user(self, token_id: UUID4) -> TokenUser:
        try:
            return await self.repository.change_one(self.session, token_id, {'is_active': False})
        except ModelNoFoundException:
            raise TokenUserNoFoundException
