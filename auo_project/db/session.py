from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.core.config import settings

engine = create_async_engine(
    settings.ASYNC_DATABASE_URI,
    echo=settings.DATABASE_ECHO,
    future=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_POOL_SIZE + 5,
)
# engine = create_async_engine(
#     settings.ASYNC_DATABASE_URI,
#     echo=True,
#     future=True,
#     pool_size=settings.DB_POOL_SIZE,
#     max_overflow=settings.DB_POOL_SIZE + 5,
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
