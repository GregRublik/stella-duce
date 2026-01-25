from uuid import UUID
from typing import Optional
from fastapi import Depends, HTTPException, status, Cookie, Response
from jwt.exceptions import ExpiredSignatureError

from services.auth import AuthService
from depends import get_auth_service
from constance import constants


async def get_current_user_id(
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),

    access_token: Optional[str] = Cookie(None, alias=constants.auth.ACCESS_TOKEN_NAME),
    refresh_token: Optional[str] = Cookie(None, alias=constants.auth.REFRESH_TOKEN_NAME),
) -> str:
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User unauthorized",
        )

    try:
        payload = auth_service.decode_jwt(access_token)
        return payload["sub"]

    except ExpiredSignatureError:
        try:
            payload = auth_service.decode_jwt(refresh_token)

            is_valid = await auth_service.validate_refresh_token(
                refresh_token,
                payload["jti"],
            )
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                )

            # ротация refresh
            await auth_service.rotate_refresh_token(UUID(payload["jti"]))

            new_access = await auth_service.create_token(payload["sub"], "access")
            new_refresh = await auth_service.create_token(payload["sub"], "refresh")

            response.set_cookie(
                constants.auth.ACCESS_TOKEN_NAME,
                new_access,
                httponly=True,
                samesite="lax",
            )
            response.set_cookie(
                constants.auth.REFRESH_TOKEN_NAME,
                new_refresh,
                httponly=True,
                samesite="lax",
            )

            return payload["sub"]

        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired",
            )
