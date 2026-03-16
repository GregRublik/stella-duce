from fastapi import APIRouter, Depends
from fastapi import status

from constance import constants
from schemas.auth import UserLogin, UserCreate
from depends import get_auth_service, get_user_service, get_otp_service, get_notification_service
from typing import Annotated
from services.auth import AuthService
from services.notification import NotificationService
from services.otp import OTPService
from services.user import UserService
from exceptions import UserNoFoundException, UserAlreadyExistsException
from fastapi.responses import Response
from exceptions import APIException
from response import ok

router = APIRouter(tags=["Auth"], prefix="/auth")


@router.post("/login")
async def auth_login(
        user: UserLogin,
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        response: Response,
):
    try:
        user_db = await user_service.get_user_by_login(user)

        if await auth_service.validate_password(user.password, user_db.password):

            access = await auth_service.create_token(user_db.id, 'access') # noqa
            refresh = await auth_service.create_token(user_db.id, 'refresh')

            response.set_cookie(constants.auth.REFRESH_TOKEN_NAME, refresh)
            response.set_cookie(constants.auth.ACCESS_TOKEN_NAME, access)

            return ok({'access_token': access, 'refresh_token': refresh})

        else:
            raise APIException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                error="Invalid username or password."
            )

    except UserNoFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )


@router.post("/register")
async def register(
        user: UserCreate,
        user_service: Annotated[UserService, Depends(get_user_service)],
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        otp_service: Annotated[OTPService, Depends(get_otp_service)],
        notification_service: Annotated[NotificationService, Depends(get_notification_service)],
        response: Response
):
    user.password = auth_service.hashing_password(user.password)

    try:

        new_user = await user_service.add_user(user)
        new_otp = await otp_service.add_otp(new_user)

        await notification_service.send_notification(new_user, new_otp, type_notification="email")


        access = await auth_service.create_token(new_user.id, 'access') # noqa
        refresh = await auth_service.create_token(new_user.id, 'refresh')

        response.set_cookie(constants.auth.REFRESH_TOKEN_NAME, refresh)
        response.set_cookie(constants.auth.ACCESS_TOKEN_NAME, access)



        # TODO Надо правильно настроить хранение токенов
        # httponly=True,  # Запрещает доступ к кукам через JavaScript (через document.cookie).
        # secure=settings.jwt.secure_cookies,  # Куки будут передаваться только по HTTPS соединению.
        # samesite=settings.jwt.same_site  # Контролирует отправку кук при "меж сайтовых" запросах. (Strict|Lax|None)

        return ok({'access_token': access, 'refresh_token': refresh})

    except UserAlreadyExistsException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )
