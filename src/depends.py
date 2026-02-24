from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from db.database import get_db_session

from services import user, auth, goal, unit_of_work

from repositories.token import TokenUserRepository
from repositories.user import UserRepository
from repositories.goal import GoalRepository


def get_user_repository() -> UserRepository:
    return UserRepository()

def get_token_user_repository() -> TokenUserRepository:
    return TokenUserRepository()

def get_goal_repository() -> GoalRepository:
    return GoalRepository()

def get_uow_service(
    session: AsyncSession = Depends(get_db_session),
) -> unit_of_work.UnitOfWork:
    return unit_of_work.UnitOfWork(session)


def get_auth_service(
    uow: unit_of_work.UnitOfWork = Depends(get_uow_service),
    repository: TokenUserRepository = Depends(get_token_user_repository)
) -> auth.AuthService:
    return auth.AuthService(repository, uow)

def get_goal_service(
    uow: unit_of_work.UnitOfWork = Depends(get_uow_service),
    repository: GoalRepository = Depends(get_goal_repository)
) -> goal.GoalService:
    return goal.GoalService(repository, uow)


def get_user_service(
    uow: unit_of_work.UnitOfWork = Depends(get_uow_service),
    repository: UserRepository = Depends(get_user_repository)
) -> user.UserService:
    return user.UserService(repository, uow)
