from fastapi import APIRouter, Depends
from dependencies.auth import get_current_user
from models.user import User
from typing import Annotated


router = APIRouter(prefix="/editor", tags=["editor"])


@router.get("/goals")
async def get_goals(
        user: Annotated[User, Depends(get_current_user)],
):
    return user.id
