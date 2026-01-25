from fastapi import Depends, HTTPException, status
from services.user import UserService
from depends import get_user_service
from models.user import User

from dependencies.auth import get_current_user_id


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
) -> User:
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
