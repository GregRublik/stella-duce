import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal, Dict, Any, Optional
import jwt
import hashlib
from uuid import UUID
from sqlalchemy.exc import NoResultFound

from config import settings
from constance import constants
from models.user import TokenUser
import bcrypt
from schemas.token import TokenUserCreate, TokenUserUpdate
from repositories.token import TokenUserRepository
from exceptions import (
    TokenUserAlreadyExistsException,
    ModelAlreadyExistsException,
    TokenUserNoFoundException,
    ModelNoFoundException
)
from services.unit_of_work import UnitOfWork


class AuthService:

    def __init__(self, repository: TokenUserRepository, uow: UnitOfWork):
        self.repository = repository
        self.uow = uow

    @staticmethod
    def decode_jwt(
            token: str,
            public_key: str = settings.auth.public_key.read_text(),
            algorithm: str = constants.auth.ALGORITHM,
    ) -> dict:
        decoded = jwt.decode(
            token,
            public_key,
            algorithms=[algorithm],
            options={"verify_sub": False}
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

    async def create_token(
            self,
            user_id: int,
            type_token: Literal['access', 'refresh']
    ) -> str:

        expires_map = {
            'access': constants.auth.EXPIRE_ACCESS_TOKEN,
            'refresh': constants.auth.EXPIRE_REFRESH_TOKEN,
        }

        token_id = uuid.uuid4()
        expires_delta = expires_map[type_token]

        token = self.encode_jwt(
            {
                'sub': user_id,
                'jti': str(token_id),
            },
            expires_delta,
            private_key=settings.auth.private_key.read_text(),
        )

        if type_token == 'refresh':
            hashed_token = self.hashing_token(token)

            token_data = {
                'id': token_id,
                'user_id': user_id,
                'token_hash': hashed_token,
                'expires_at': datetime.now(timezone.utc) + + timedelta(seconds=expires_delta)

            }

            await self.repository.add_one(self.uow.session, token_data)

        return token

    @staticmethod
    def hashing_password(
            hashing_string: str,
    ) -> bytes:
        salt = bcrypt.gensalt()
        pwd_bytes: bytes = hashing_string.encode()
        return bcrypt.hashpw(pwd_bytes, salt)

    @staticmethod
    async def validate_password(
            password: str,
            hashed_password: bytes,
    ) -> bool:
        return bcrypt.checkpw(
            password=password.encode(),
            hashed_password=hashed_password,
        )

    @staticmethod
    def hashing_token(
            token: str,
    ) -> bytes:
        """Хеширование токена для хранения в БД"""
        # Используем SHA-256, у него нет ограничения на длину
        return hashlib.sha256(token.encode()).digest()

    async def validate_refresh_token(self, token: str, token_id: str) -> bool:
        try:
            token_db = await self.repository.get_by_id(self.uow.session, UUID(token_id))

            if token_db.is_expired:
                return False

            if token_db.token_hash != self.hashing_token(token):
                return False

            # Если токен ещё не использовался
            if token_db.rotated_at is None:
                return True

            # Если использован — проверяем grace-period
            grace_deadline = token_db.rotated_at + timedelta(seconds=constants.auth.REFRESH_GRACE_SECONDS)

            return datetime.now(timezone.utc) <= grace_deadline

        except ModelNoFoundException:
            return False

    async def add_token_user(self, token: TokenUserCreate) -> TokenUser:
        try:
            return await self.repository.add_one(self.uow.session, token.model_dump())
        except ModelAlreadyExistsException:
            raise TokenUserAlreadyExistsException


    async def update_by_id(self, token: TokenUserUpdate) -> TokenUser:
        try:
            return await self.repository.update_by_id(self.uow.session, token)
        except NoResultFound:
            raise TokenUserNoFoundException

    async def deactivate_token_user(self, token_id: UUID) -> TokenUser:
        try:
            return await self.repository.change_one(self.uow.session, token_id, {'is_active': False})
        except ModelNoFoundException:
            raise TokenUserNoFoundException

    async def rotate_refresh_token(self, token_id: UUID) -> None:
        try:
            await self.repository.change_one(
                self.uow.session,
                token_id,
                {'rotated_at': datetime.now(timezone.utc)},
            )
        except ModelNoFoundException:
            raise TokenUserNoFoundException

