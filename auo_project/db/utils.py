from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from auo_project.core.config import settings


def get_url(db_name="template1"):
    return f"postgresql+asyncpg://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{db_name}"


def get_engine(dbname):
    db_url = get_url(dbname)
    conn_args = {}
    if settings.DATABASE_SSL_REQURED:
        conn_args["ssl"] = "require"
    engine = create_async_engine(
        db_url,
        connect_args=conn_args,
        isolation_level="AUTOCOMMIT",
    )
    return engine


async def drop_conn(dbname, engine):
    async with engine.connect() as conn:
        await conn.execute(
            text(
                f"SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{dbname}' AND pid <> pg_backend_pid();",  # noqa: E501, S608
            ),
        )


async def create_database(dbname, engine=None) -> None:
    """Create a databse."""
    if not engine:
        engine = get_engine("template1")

    async with engine.connect() as conn:
        database_existance = await conn.execute(
            text(
                f"SELECT 1 FROM pg_database WHERE datname='{dbname}'",  # noqa: E501, S608
            ),
        )
        database_exists = database_existance.scalar() == 1

    if database_exists:
        await drop_conn(dbname, engine)
        await drop_database(dbname)

    postgres_engine = get_engine("postgres")
    await drop_conn("template1", postgres_engine)
    async with postgres_engine.connect() as conn:  # noqa: WPS440
        await conn.execute(
            text(
                f'CREATE DATABASE "{dbname}" ENCODING "utf8" TEMPLATE template1;',  # noqa: E501
            ),
        )

    engine = get_engine(dbname)
    async with engine.connect() as conn:  # noqa: WPS440
        await conn.execute(
            text(
                f'CREATE SCHEMA IF NOT EXISTS "app"',  # noqa: E501
            ),
        )
        await conn.execute(
            text(
                f'CREATE SCHEMA IF NOT EXISTS "measure"',  # noqa: E501
            ),
        )
        await conn.commit()
        schemas = await conn.execute(
            text(
                "select schema_name from information_schema.schemata;",
            ),
        )
        print(schemas.fetchall())


async def drop_database(dbname, engine=None) -> None:
    """Drop current database."""
    if not engine:
        engine = get_engine("template1")
    async with engine.connect() as conn:
        disc_users = (
            "SELECT pg_terminate_backend(pg_stat_activity.pid) "  # noqa: S608
            "FROM pg_stat_activity "
            f"WHERE pg_stat_activity.datname = '{dbname}' "
            "AND pid <> pg_backend_pid();"
        )
        await conn.execute(text(disc_users))
        await conn.execute(text(f'DROP DATABASE IF EXISTS "{dbname}"'))
