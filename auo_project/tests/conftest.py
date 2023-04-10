import asyncio
import os
from typing import Any, AsyncGenerator, Generator

import pytest
from fakeredis import FakeServer
from fakeredis.aioredis import FakeConnection
from fastapi import FastAPI
from httpx import AsyncClient
from redis.asyncio import ConnectionPool
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker

from auo_project.core.config import settings
from auo_project.db.dependencies import get_db_session
from auo_project.db.init_db import init_db
from auo_project.db.utils import create_database, drop_database, get_engine
from auo_project.services.redis.dependency import get_redis_pool
from auo_project.tests.utils import AuthTestClient
from auo_project.web.api.deps import get_db
from auo_project.web.application import get_app

ENVIRONMENT = "testing"
os.environ["ENVIRONMENT"] = ENVIRONMENT
settings.ENVIRONMENT = ENVIRONMENT


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.

    :return: backend name.
    """
    return "asyncio"


@pytest.fixture
def asyncio_event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.DefaultEventLoopPolicy().new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    asyncio.set_event_loop(None)
    loop.close()


@pytest.fixture(scope="session")
async def _engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create engine and databases.

    :yield: new engine.
    """
    from auo_project.db.meta import meta  # noqa: WPS433
    from auo_project.models import load_all_models  # noqa: WPS433

    load_all_models()

    dbname = (
        f"{settings.DATABASE_NAME}_testing"
        if settings.ENVIRONMENT == "testing"
        else settings.DATABASE_NAME
    )
    from auo_project.db.session import engine

    engine = get_engine(dbname)
    try:
        yield engine
    finally:
        await engine.dispose()
        await drop_database(dbname)


@pytest.fixture
async def db_session(
    _engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get session to database.

    Fixture that returns a SQLAlchemy session with a SAVEPOINT, and the rollback to it
    after the test completes.

    :param _engine: current engine.
    :yields: async session.
    """
    connection = await _engine.connect()
    trans = await connection.begin()

    session_maker = sessionmaker(
        bind=connection,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    session = session_maker()

    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()
        # close and clean-up pooled connections
        await _engine.dispose()


@pytest.fixture
async def fake_redis_pool() -> AsyncGenerator[ConnectionPool, None]:
    """
    Get instance of a fake redis.

    :yield: FakeRedis instance.
    """
    server = FakeServer()
    server.connected = True
    pool = ConnectionPool(connection_class=FakeConnection, server=server)

    yield pool

    await pool.disconnect()


@pytest.fixture
def fastapi_app(
    db_session: AsyncSession,
    fake_redis_pool: ConnectionPool,
) -> FastAPI:
    """
    Fixture for creating FastAPI app.

    :return: fastapi app with mocked dependencies.
    """
    application = get_app()
    print("application start", application)
    application.dependency_overrides[get_db] = lambda: db_session
    application.dependency_overrides[get_db_session] = lambda: db_session
    application.dependency_overrides[get_redis_pool] = lambda: fake_redis_pool
    print("application end", application)
    return application  # noqa: WPS331


@pytest.fixture
async def client(
    fastapi_app: FastAPI,
    anyio_backend: Any,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates client for requesting server.

    :param fastapi_app: the application.
    :yield: client for the app.
    """
    async with AuthTestClient(app=fastapi_app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
async def initialize_db() -> AsyncGenerator[None, None]:
    """
    Create models and databases.
    :yield: new engine.
    """
    from auo_project.db.meta import meta  # noqa: WPS433
    from auo_project.models import load_all_models  # noqa: WPS433

    load_all_models()

    dbname = (
        f"{settings.DATABASE_NAME}_testing"
        if settings.ENVIRONMENT == "testing"
        else settings.DATABASE_NAME
    )
    await create_database(dbname)

    engine = get_engine(dbname)
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)
        local_session = sessionmaker(
            bind=conn,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )
        await init_db(db_session=local_session())
        await conn.commit()

    yield

    await engine.dispose()
    await drop_database(dbname)
