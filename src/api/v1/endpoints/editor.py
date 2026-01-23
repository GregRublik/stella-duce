from fastapi import APIRouter, Depends, HTTPException, Cookie, status
from fastapi.responses import Response
from depends import get_auth_service, get_user_service
from dependencies.auth import get_current_user
from models.user import User
from constance import constants
from jwt.exceptions import ExpiredSignatureError
from typing import Annotated

from services.auth import AuthService
from services.user import UserService

router = APIRouter(prefix="/editor", tags=["editor"])


@router.get("/goals")
async def get_goals(
        user: Annotated[User, Depends(get_current_user)],
):
    return