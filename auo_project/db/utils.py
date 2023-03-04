from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from auo_project.core.config import settings


def get_url():
    # return  make_url(str(f"postgresql+asyncpg://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}"))
    return settings.ASYNC_DATABASE_URI


def get_engine():
    db_url = get_url()
    conn_args = {}
    if settings.DATABASE_SSL_REQURED:
        conn_args["ssl"] = "require"
    engine = create_async_engine(
        db_url,
        connect_args=conn_args,
        isolation_level="AUTOCOMMIT",
    )
    return engine


async def create_database(engine=None) -> None:
    """Create a databse."""
    dbname = (
        f"{settings.DATABASE_NAME}_testing"
        if settings.ENVIRONMENT == "testing"
        else settings.DATABASE_NAME
    )

    if not engine:
        engine = get_engine()

    async with engine.connect() as conn:
        database_existance = await conn.execute(
            text(
                f"SELECT 1 FROM pg_database WHERE datname='{dbname}'",  # noqa: E501, S608
            ),
        )
        database_exists = database_existance.scalar() == 1

    if database_exists:
        await drop_database()

    async with engine.connect() as conn:  # noqa: WPS440
        await conn.execute(
            text(
                f'CREATE DATABASE "{dbname}" ENCODING "utf8" TEMPLATE template1;',  # noqa: E501
            ),
        )

    engine = get_engine()
    async with engine.connect() as conn:  # noqa: WPS440
        await conn.execute(
            text(
                f'CREATE SCHEMA IF NOT EXISTS "app"',  # noqa: E501
            ),
        )


async def drop_database(engine=None) -> None:
    """Drop current database."""
    dbname = (
        f"{settings.DATABASE_NAME}_testing"
        if settings.ENVIRONMENT == "testing"
        else settings.DATABASE_NAME
    )
    if not engine:
        engine = get_engine()
    async with engine.connect() as conn:
        disc_users = (
            "SELECT pg_terminate_backend(pg_stat_activity.pid) "  # noqa: S608
            "FROM pg_stat_activity "
            f"WHERE pg_stat_activity.datname = '{dbname}' "
            "AND pid <> pg_backend_pid();"
        )
        await conn.execute(text(disc_users))
        await conn.execute(text(f'DROP DATABASE "{dbname}"'))


def load_all_models():
    pass
