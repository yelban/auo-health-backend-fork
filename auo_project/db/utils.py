from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

# from auo_project.settings import settings
from auo_project.core.config import settings


async def create_database(engine=None) -> None:
    """Create a databse."""
    dbname = (
        f"{settings.DATABASE_NAME}_testing"
        if settings.ENVIRONMENT == "testing"
        else settings.DATABASE_NAME
    )

    if not engine:
        db_url = make_url(
            str(f"postgresql+asyncpg://auo_project:auo_project@auo_project-db:5432"),
        )
        engine = create_async_engine(db_url, isolation_level="AUTOCOMMIT")

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

    db_url = make_url(
        str(
            f"postgresql+asyncpg://auo_project:auo_project@auo_project-db:5432/{dbname}",
        ),
    )
    engine = create_async_engine(db_url, isolation_level="AUTOCOMMIT")
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
        db_url = make_url(
            str(f"postgresql+asyncpg://auo_project:auo_project@auo_project-db:5432"),
        )
        engine = create_async_engine(db_url, isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        disc_users = (
            "SELECT pg_terminate_backend(pg_stat_activity.pid) "  # noqa: S608
            "FROM pg_stat_activity "
            f"WHERE pg_stat_activity.datname = '{dbname}' "
            "AND pid <> pg_backend_pid();"
        )
        await conn.execute(text(disc_users))
        await conn.execute(text(f'DROP DATABASE "{dbname}" WITH (FORCE)'))
