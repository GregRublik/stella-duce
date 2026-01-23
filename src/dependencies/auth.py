from fastapi import Depends, HTTPException, status, Cookie, Response
from typing import Annotated, Optional, Tuple
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from schemas.token import TokenUserUpdate
from services.auth import AuthService
from services.token import TokenService
from services.user import UserService

from depends import get_auth_service, get_user_service, get_token_service
from models.user import User
from constance import constants


async def get_current_user(
        response: Response,
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        token_service: Annotated[TokenService, Depends(get_token_service)],
        access_token: Optional[str] = Cookie(None, alias=constants.auth.ACCESS_TOKEN_NAME),
        refresh_token: Optional[str] = Cookie(None, alias=constants.auth.REFRESH_TOKEN_NAME),
) -> Tuple[User, Optional[str], Optional[str]]:
    """
    Возвращает пользователя и обновленные токены (если были обновлены)
    """
    if not access_token or not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User unauthorized"
        )

    updated_tokens = None

    try:
        # Пробуем декодировать access токен
        payload = auth_service.decode_jwt(access_token)
        user_id = payload.get("sub")

    except ExpiredSignatureError:
        try:
            # Если access токен истек, пробуем обновить через refresh
            payload = auth_service.decode_jwt(refresh_token)
            user_id = payload.get("sub")

            # Проверяем валидность refresh токена в БД
            is_valid = await token_service.validate_refresh_token(refresh_token, user_id)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )

            user_db = await user_service.get_user_by_id(user_id)

            # Генерируем новые токены
            new_access_token = await auth_service.create_token(user_db, 'access')
            new_refresh_token = await auth_service.create_token(user_db, 'refresh')

            await auth_service.deactivate_token(payload.get("jti"))



        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired"
            )

            # Устанавливаем обновленные токены в куки
            response.set_cookie(
                constants.auth.ACCESS_TOKEN_NAME,
                new_access_token,
                httponly=True,
                secure=True,
                samesite="lax"
            )
            response.set_cookie(
                constants.auth.REFRESH_TOKEN_NAME,
                new_refresh_token,
                httponly=True,
                secure=True,
                samesite="lax"
            )

    # Получаем пользователя из БД
    user = await user_service.get_user(user_id)

    return user, new_access_token, new_refresh_token
