from repositories.token import TokenUserRepository
from services import user, auth
from repositories.user import UserRepository
from db.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends


def get_user_repository() -> UserRepository:
    return UserRepository()

def get_token_user_repository() -> TokenUserRepository:
    return TokenUserRepository()

def get_auth_service(
    session: AsyncSession = Depends(get_db_session),
    repository: TokenUserRepository = Depends(get_token_user_repository)
) -> auth.AuthService:
    return auth.AuthService(
        repository, session
    )

def get_user_service(
    session: AsyncSession = Depends(get_db_session),
    repository: UserRepository = Depends(get_user_repository)
) -> user.UserService:
    return user.UserService(repository, session)
