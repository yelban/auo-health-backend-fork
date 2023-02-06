from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.core.config import settings

conn_args = {}
if settings.DATABASE_SSL_REQURED:
    conn_args["ssl"] = "require"

engine = create_async_engine(
    settings.ASYNC_DATABASE_URI,
    echo=settings.DATABASE_ECHO,
    future=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_POOL_SIZE + 5,
    connect_args=conn_args,
)
# engine = create_async_engine(
#     settings.ASYNC_DATABASE_URI,
#     echo=True,
#     future=True,
#     pool_size=settings.DB_POOL_SIZE,
#     max_overflow=settings.DB_POOL_SIZE + 5,
#     connect_args=conn_args,
# )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async_session_factory = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

mixins_session = scoped_session(sessionmaker(bind=engine, autocommit=True))
