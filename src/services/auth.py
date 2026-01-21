from datetime import datetime, timedelta, timezone
from typing import Literal, Dict, Any, Optional
import jwt
from config import settings
from constance import constants
from models.user import User

class AuthService:

    @staticmethod
    async def encode_jwt(
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

        if type_token == 'access':
            expire_time = constants.auth.EXPIRE_ACCESS_TOKEN
        else:
            expire_time = constants.auth.EXPIRE_REFRESH_TOKEN

        return await self.encode_jwt(
            {
                'sub': user.id,
            },
            expire_time,
            private_key=settings.auth.private_key.read_text(),
        )


    async def get_tokens(self, user: User):

        access = await self.create_token(user, type_token="access")
        refresh = await self.create_token(user, type_token="refresh")

        return access, refresh
