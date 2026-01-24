from pathlib import Path

class AuthConstants:
    """Константы авторизации"""

    ACCESS_TOKEN_NAME: str = "stella-duce-access-token"
    REFRESH_TOKEN_NAME: str = "stella-duce-refresh-token"

    EXPIRE_ACCESS_TOKEN: int = 30
    EXPIRE_REFRESH_TOKEN: int = 43200
    REFRESH_GRACE_SECONDS: int = 10

    ALGORITHM: str = "RS256"

class AppConstants:
    """Константы приложения"""

    BASE_DIR = Path(__file__).parent.parent


    def __init__(self, auth: AuthConstants):
        self.auth = auth



constants = AppConstants(
    AuthConstants()
)
