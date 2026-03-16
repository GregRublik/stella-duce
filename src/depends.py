from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from db.database import get_db_session
from repositories.otp import OTPRepository

from services import user, auth, goal, unit_of_work, goal_stage, otp, notification

from repositories.token import TokenUserRepository
from repositories.user import UserRepository
from repositories.goal import GoalRepository
from repositories.goal_stage import GoalStageRepository
from repositories.stage_dependency import StageDependencyRepository


# REPOSITORIES
def get_user_repository() -> UserRepository:
    return UserRepository()

def get_otp_repository() -> OTPRepository:
    return OTPRepository()

def get_token_user_repository() -> TokenUserRepository:
    return TokenUserRepository()

def get_goal_repository() -> GoalRepository:
    return GoalRepository()

def get_goal_stage_repository() -> GoalStageRepository:
    return GoalStageRepository()

def get_stage_dependency_repository() -> StageDependencyRepository:
    return StageDependencyRepository()


# SERVICES
def get_uow_service(
    session: AsyncSession = Depends(get_db_session),
) -> unit_of_work.UnitOfWork:
    return unit_of_work.UnitOfWork(session)

def get_auth_service(
    uow: unit_of_work.UnitOfWork = Depends(get_uow_service),
    repository: TokenUserRepository = Depends(get_token_user_repository)
) -> auth.AuthService:
    return auth.AuthService(repository, uow)

def get_otp_service(
    uow: unit_of_work.UnitOfWork = Depends(get_uow_service),
    repository: OTPRepository = Depends(get_otp_repository),
) -> otp.OTPService:
    return otp.OTPService(repository, uow)

def get_notification_service(

) -> notification.NotificationService:
    return notification.NotificationService()

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

def get_goal_stage_service(
    uow: unit_of_work.UnitOfWork = Depends(get_uow_service),
    repository: GoalStageRepository = Depends(get_goal_stage_repository),
    goal_repository: GoalRepository = Depends(get_goal_repository),
    stage_dependency_repository: StageDependencyRepository = Depends(get_stage_dependency_repository)
) -> goal_stage.GoalStageService:
    return goal_stage.GoalStageService(repository, goal_repository, stage_dependency_repository, uow)
