import enum
import os
import secrets
from pathlib import Path
from tempfile import gettempdir
from typing import Any, Callable, Dict, List, Optional, Union

from cryptography.fernet import Fernet
from pydantic import (
    AnyHttpUrl,
    BaseSettings,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    RedisDsn,
    validator,
)

TEMP_DIR = Path(gettempdir())


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # quantity of workers for uvicorn
    WORKERS_COUNT: int = 1
    # Enable uvicorn reloading
    RELOAD: bool = False

    # Current environment
    ENVIRONMENT: str = "dev"

    LOG_LEVEL: LogLevel = LogLevel.INFO

    NEED_INIT_DATA: bool = False

    API_VERSION: str = "v1"
    API_V1_STR: str = f"/api/{API_VERSION}"
    PROJECT_NAME: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30

    # Variables for the database
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: Union[int, str]
    DATABASE_NAME: str
    DATABASE_SSL_REQURED: bool
    DATABASE_ECHO: bool = False

    # Variables for Redis
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_USER: Optional[str] = None
    REDIS_PASS: Optional[str] = None
    REDIS_BASE: Optional[int] = None

    RABBITMQ_HOSTNAME: str
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_DEFAULT_VHOST: str

    DB_POOL_SIZE = 83
    POOL_SIZE = max(DB_POOL_SIZE // WORKERS_COUNT, 5)
    ASYNC_DATABASE_URI: Optional[str]

    @validator("ASYNC_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("DATABASE_USER"),
            password=values.get("DATABASE_PASSWORD"),
            host=values.get("DATABASE_HOST"),
            port=str(values.get("DATABASE_PORT")),
            path=f"/{values.get('DATABASE_NAME') or ''}",
        )

    REDIS_DATABASE_URI: Optional[str]

    @validator("REDIS_DATABASE_URI", pre=True)
    def assemble_redis_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return RedisDsn.build(
            scheme="redis",
            user=values.get("REDIS_USER"),
            password=values.get("REDIS_PASS"),
            host=values.get("REDIS_HOST"),
            port=str(values.get("REDIS_PORT")),
            path=f"/{values.get('REDIS_BASE') or ''}",
        )

    FIRST_SUPERUSER_ORG_NAME: str
    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    MAX_SIZE_PER_UPLOAD: int = 1000
    MAX_SIZE_PER_FILE: int = 100
    ROWS_PER_PAGE: int = 500
    MAX_ROWS_PER_PAGE: int = 500
    MAX_UPLOAD_CONCURRENCY: int = 20

    AZURE_STORAGE_ACCOUNT: str
    AZURE_STORAGE_KEY: str
    AZURE_STORAGE_CONTAINER: str
    AZURE_STORAGE_CONTAINER_RAW_ZIP: str

    AZURE_STORAGE_ACCOUNT_INTERNET: str
    AZURE_STORAGE_KEY_INTERNET: str
    AZURE_STORAGE_CONTAINER_INTERNET_IMAGE: str

    SECRET_KEY: str = secrets.token_urlsafe(32)
    ENCRYPT_KEY: str = Fernet.generate_key()
    TXT_FILE_AES_KEY: bytes

    @validator("TXT_FILE_AES_KEY", pre=True)
    def convert_aes_key_bytes(cls, v: str) -> bytes:
        if isinstance(v, str):
            return bytes.fromhex(v)
        return v

    TXT_FILE_AES_IV: bytes

    @validator("TXT_FILE_AES_IV", pre=True)
    def convert_aes_iv_bytes(cls, v: str) -> bytes:
        if isinstance(v, str):
            return bytes.fromhex(v)
        return v

    BACKEND_CORS_ORIGINS: Union[List[str], List[AnyHttpUrl]]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    BACKEND_CORS_REGEX: str = None

    # This variable is used to define
    # multiproc_dir. It's required for [uvi|guni]corn projects.
    PROMETHEUS_DIR: Path = TEMP_DIR / "prom"

    # Sentry's configuration.
    SENTRY_DSN_BACKEND: Optional[HttpUrl] = None
    SENTRY_SAMPLE_RATE_BACKEND: float = 1.0

    @validator("SENTRY_DSN_BACKEND", pre=True)
    def sentry_dsn_backend_can_be_blank(cls, v: str) -> Optional[str]:
        if len(v) == 0:
            return None
        return v

    # Grpc endpoint for opentelemetry.
    # E.G. http://localhost:4317
    OPENTELEMETRY_ENDPOINT: Optional[str] = None

    class Config:
        case_sensitive = True
        env_file = ".env", "/mnt/secrets-store/.env"
        # `/mnt/secrets-store/.env` takes priority over `.env`
        env_file_encoding = "utf-8"
        # secrets_dir = '/mnt/secrets-store'


class AuthConfig:
    _token = None
    _denylist_token_checks = {"access", "refresh"}
    _algorithm = "HS256"
    _denylist_enabled = False
    _denylist_token_checks = {"access", "refresh"}
    _header_name = "Authorization"
    _header_type = "Bearer"
    # _access_token_expires = timedelta(minutes=15)
    # _refresh_token_expires = timedelta(days=30)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30

    # option for create cookies
    _access_cookie_key = "access_token_cookie"
    _refresh_cookie_key = "refresh_token_cookie"
    _access_cookie_path = "/"
    _refresh_cookie_path = "/"
    _cookie_max_age = None
    _cookie_domain = None
    # _cookie_domain = "*.deepinsight.tw" if os.getenv('ENVIRONMENT') != "dev" else None
    _cookie_secure = True
    # _cookie_secure = True if os.getenv('ENVIRONMENT') != "dev" else None
    _cookie_samesite = "Lax" if os.getenv("ENVIRONMENT") != "dev" else "none"

    # option for double submit csrf protection
    _cookie_csrf_protect = True
    _access_csrf_cookie_key = "csrf_access_token"
    _refresh_csrf_cookie_key = "csrf_refresh_token"
    _access_csrf_cookie_path = "/"
    _refresh_csrf_cookie_path = "/"
    _access_csrf_header_name = "X-CSRF-Token"
    _refresh_csrf_header_name = "X-CSRF-Token"
    _csrf_methods = {"POST", "PUT", "PATCH", "DELETE"}

    @classmethod
    def token_in_denylist_loader(cls, callback: Callable[..., bool]) -> "AuthConfig":
        """
        This decorator sets the callback function that will be called when
        a protected endpoint is accessed and will check if the JWT has been
        been revoked. By default, this callback is not used.
        *HINT*: The callback must be a function that takes decrypted_token argument,
        args for object AuthJWT and this is not used, decrypted_token is decode
        JWT (python dictionary) and returns *`True`* if the token has been deny,
        or *`False`* otherwise.
        """
        cls._token_in_denylist_callback = callback

    class Config:
        case_sensitive = True
        # `/mnt/secrets-store/.env` takes priority over `.env`
        env_file = ".env", "/mnt/secrets-store/.env"
        # env_file = ".env"
        env_file_encoding = "utf-8"
        # secrets_dir = '/mnt/secrets-store'


settings = Settings()
