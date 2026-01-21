from aiohttp import ClientSession
from pydantic_settings import SettingsConfigDict, BaseSettings
from fastapi.templating import Jinja2Templates
from pathlib import Path

from constance import constants


class SessionManager:
    _session: ClientSession | None = None

    @classmethod
    async def get_session(cls) -> ClientSession:
        """Возвращает сессию aiohttp, создавая её при первом вызове."""
        if cls._session is None or cls._session.closed:
            cls._session = ClientSession()
        return cls._session

    @classmethod
    async def close_session(cls):
        """Закрывает сессию, если она существует."""
        if cls._session is not None:
            await cls._session.close()
            cls._session = None


class QueueSettings(BaseSettings):
    pass


class RabbitSettings(BaseSettings):
    user: str
    password: str
    host: str
    port: int

    # queues: QueueSettings

    @property
    def url(self) -> str:
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="RABBITMQ_",
        extra="ignore"
    )


class AuthSettings(BaseSettings):

    public_key: Path = constants.BASE_DIR / 'public_key.pem'
    private_key: Path = constants.BASE_DIR / 'private_key.pem'

    model_config = SettingsConfigDict(env_prefix="AUTH_", env_file=".env", extra="ignore")


class DbSettings(BaseSettings):
    host: str
    user: str
    password: str
    name: str
    port: int

    model_config = SettingsConfigDict(env_prefix="DB_", env_file=".env", extra="ignore")

    @property
    def dsn_asyncpg(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

class Settings(BaseSettings):
    port: int
    host: str

    auth: AuthSettings
    db: DbSettings
    rabbitmq: RabbitSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        extra="ignore"
    )

templates = Jinja2Templates(directory="src/templates")

settings = Settings(
    db=DbSettings(),
    rabbitmq=RabbitSettings(),
    auth=AuthSettings(),
)
