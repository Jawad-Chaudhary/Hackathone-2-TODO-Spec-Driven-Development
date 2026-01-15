# [Task]: T-010
# [From]: specs/001-ai-todo-chatbot/plan.md

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from .connection import engine


# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for getting database sessions.

    Yields:
        AsyncSession: Database session for use in endpoints

    Example:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_db_session)):
            result = await session.execute(select(Item))
            return result.scalars().all()
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
