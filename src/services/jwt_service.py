class JWTService:

    @staticmethod
    async def create_access_token(user: User):
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "type": "access"
        }
        return await encode_jwt(payload, 1)

    @staticmethod
    async def create_refresh_token(user: User):
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "type": "refresh"
        }
        return await encode_jwt(payload, 43200)

    @staticmethod
    async def validate_password(
            password: str,
            hashed_password: bytes,
    ) -> bool:
        return bcrypt.checkpw(
            password=password.encode(),
            hashed_password=hashed_password,
        )
