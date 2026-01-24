from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from constance import constants
from schemas.auth import UserLogin, UserCreate
from depends import get_auth_service, get_user_service
from typing import Annotated, List, Literal
from services.auth import AuthService
from services.user import UserService
from exceptions import UserNoFoundException, UserAlreadyExistsException
from fastapi.responses import Response
from config import settings, templates

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/login")
async def auth_login(
        user: UserLogin,
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        response: Response,
):
    try:
        user_db = await user_service.get_user_by_login(user)

        access = await auth_service.create_token(user_db, 'access')
        refresh = await auth_service.create_token(user_db, 'refresh')

        response.set_cookie(constants.auth.REFRESH_TOKEN_NAME, refresh)
        response.set_cookie(constants.auth.ACCESS_TOKEN_NAME, access)

        return {"success": True, 'data': {'access_token': access, 'refresh_token': refresh}}
    except UserNoFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "error": e.detail}
        )


@router.post("/register")
async def register(
        user: UserCreate,
        user_service: Annotated[UserService, Depends(get_user_service)],
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        response: Response
):
    user.password = auth_service.hashing_password(user.password)

    try:

        new_user = await user_service.add_user(user)

        access = await auth_service.create_token(new_user, 'access')
        refresh = await auth_service.create_token(new_user, 'refresh')

        response.set_cookie(constants.auth.REFRESH_TOKEN_NAME, refresh)
        response.set_cookie(constants.auth.ACCESS_TOKEN_NAME, access)

        # TODO Надо правильно настроить хранение токенов
        # httponly=True,  # Запрещает доступ к кукам через JavaScript (через document.cookie).
        # secure=settings.jwt.secure_cookies,  # Куки будут передаваться только по HTTPS соединению.
        # samesite=settings.jwt.same_site  # Контролирует отправку кук при "меж сайтовых" запросах. (Strict|Lax|None)

        return {"success": True, 'data': {'access_token': access, 'refresh_token': refresh}}

    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"success": False, "error": e.detail}
        )
