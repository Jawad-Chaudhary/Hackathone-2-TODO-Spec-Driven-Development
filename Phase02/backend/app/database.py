# [Task T010, T013] Async database engine and initialization with SQLModel + asyncpg

from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from app.config import settings


# Create async engine for PostgreSQL with asyncpg driver
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",  # Log SQL in development
    future=True,
)

# Async session maker
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_db_and_tables():
    """
    Create all database tables based on SQLModel definitions.
    Called on application startup.
    """
    async with async_engine.begin() as conn:
        # Create all tables defined with SQLModel
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    """
    Dependency for getting async database session.
    Yields session and ensures it's closed after use.
    """
    async with AsyncSessionLocal() as session:
        yield session
