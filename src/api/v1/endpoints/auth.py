from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi import status

from constance import constants
from schemas.auth import UserLogin, UserCreate, UserVerifyEmailOtp, UserEmail, UserLoginOtp
from depends import get_auth_service, get_user_service, get_otp_service

from models.user import UserStatus

from services.auth import AuthService
from services.otp import OTPService
from services.user import UserService
from exceptions import UserNoFoundException, UserAlreadyExistsException
from fastapi.responses import Response
from exceptions import APIException
from response import ok

router = APIRouter(tags=["Auth"], prefix="/auth")


@router.post("/login-otp")
async def auth_login_otp(
        user: UserLoginOtp,
        user_service: Annotated[UserService, Depends(get_user_service)],
        otp_service: Annotated[OTPService, Depends(get_otp_service)],
):
    """Войти с помощью otp кода"""
    try:
        user_db = await user_service.get_user_by_email(user)

        await otp_service.generate_and_send(user_db)

        return ok({"message": "OTP sent to email"})

    except UserNoFoundException as e:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error=e.detail
        )


@router.post("/login")
async def auth_login(
        user: UserLogin,
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        otp_service: Annotated[OTPService, Depends(get_otp_service)]
):
    """Войти в систему"""
    try:
        user_db = await user_service.get_user_by_email(user)

        if await auth_service.validate_password(user.password, user_db.password):

            await otp_service.generate_and_send(user_db)

            return ok({"message": "OTP sent to email"})

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

@router.post("/verify-otp")
async def verify_otp(
        data: UserVerifyEmailOtp,
        user_service: Annotated[UserService, Depends(get_user_service)],
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        otp_service: Annotated[OTPService, Depends(get_otp_service)],
        response: Response
):

    user_db = await user_service.get_user_by_email(UserEmail(email=data.email))

    result_verify = await otp_service.verify(user_db, data.otp_code)

    if user_db.status == UserStatus.PENDING and result_verify:
        await user_service.change_status_user(user_db.id, UserStatus.VERIFIED)

    if result_verify:

        access = await auth_service.create_token(user_db.id, 'access')  # noqa
        refresh = await auth_service.create_token(user_db.id, 'refresh')

        # TODO Надо правильно настроить хранение токенов
        response.set_cookie(constants.auth.REFRESH_TOKEN_NAME, refresh)
        response.set_cookie(constants.auth.ACCESS_TOKEN_NAME, access)

        return ok({'access_token': access, 'refresh_token': refresh})
    else:
        raise APIException(
            status_code=400,
            error="Invalid or expired OTP code"
        )

@router.post("/register")
async def register(
        user: UserCreate,
        user_service: Annotated[UserService, Depends(get_user_service)],
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        otp_service: Annotated[OTPService, Depends(get_otp_service)]
):
    """Регистрация в системе"""
    user.password = auth_service.hashing_password(user.password)

    try:

        user_db = await user_service.add_user(user)

        await otp_service.generate_and_send(user_db)

        return ok({"message": "OTP sent to email"})

    except UserAlreadyExistsException as e:
        raise APIException(
            status_code=status.HTTP_409_CONFLICT,
            error=e.detail
        )
