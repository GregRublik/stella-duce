from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from config import settings
import jwt
import bcrypt

from schemas.users import User


async def encode_jwt(
        payload: Dict[str, Any],
        expire_minutes: int,
        private_key: str = settings.jwt.private_key_path.read_text(),
        algorithm: str = settings.jwt.algorithm,
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


async def decode_jwt(
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


class JWTService:

    @staticmethod
    async def create_access_token(user: User):
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "type": "access"
        }
        return await encode_jwt(payload, 1)

    @staticmethod
    async def create_refresh_token(user: User):
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "type": "refresh"
        }
        return await encode_jwt(payload, 43200)

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
    async def hash_password(
            password: str,
    ) -> bytes:
        salt = bcrypt.gensalt()
        pwd_bytes: bytes = password.encode()
        return bcrypt.hashpw(pwd_bytes, salt)