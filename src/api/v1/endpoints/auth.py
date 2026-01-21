from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from constance import constants
from schemas.auth import UserLogin
from depends import get_auth_service, get_user_service
from typing import Annotated
from services.auth import AuthService
from services.user import UserService
from exceptions import UserNoFoundException
from fastapi.responses import Response
from config import settings

router = APIRouter()

@router.post("/login")
async def auth_login(
        user: UserLogin,
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        response: Response,
):
    try:
        user_db = await user_service.get_user(user)
        access, refresh = await auth_service.get_tokens(user_db)

        response.set_cookie(constants.auth.REFRESH_TOKEN_NAME, refresh)
        response.set_cookie(constants.auth.ACCESS_TOKEN_NAME, access)

        return {"success": True, 'data': {'access_token': access, 'refresh_token': refresh}}
    except UserNoFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "error": e.detail}
        )
