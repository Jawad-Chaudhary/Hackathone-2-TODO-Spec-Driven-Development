# Test configuration and fixtures

import pytest
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

# Patch BEFORE importing app
_create_db_patch = patch("app.database.create_db_and_tables", new_callable=AsyncMock)
_create_db_patch.start()

# Now import app
from app.main import app
from app.config import settings
from app.database import get_session

# Global mock database session for all tests
_mock_db_session = AsyncMock()
_mock_db_session.add = MagicMock()
_mock_db_session.commit = AsyncMock()
_mock_db_session.refresh = AsyncMock()
_mock_db_session.execute = AsyncMock()


async def _mock_get_session_override():
    """Global mock session override."""
    yield _mock_db_session


# Apply overrides BEFORE creating test client
app.dependency_overrides[get_session] = _mock_get_session_override


@pytest.fixture(scope="function")
def mock_db_session_conftest():
    """Return the global mock database session."""
    return _mock_db_session


@pytest.fixture(scope="function")
def client():
    """Create a test client with already-mocked database."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_user_id():
    """Return a test user ID."""
    return "123"  # String representation of numeric user ID


@pytest.fixture
def valid_jwt_token(test_user_id):
    """Generate a valid JWT token for testing."""
    payload = {
        "sub": test_user_id,
        "user_id": test_user_id,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")
    return token


@pytest.fixture
def auth_headers(valid_jwt_token):
    """Generate authorization headers with valid JWT."""
    return {"Authorization": f"Bearer {valid_jwt_token}"}


@pytest.fixture
def expired_jwt_token(test_user_id):
    """Generate an expired JWT token for testing."""
    payload = {
        "sub": test_user_id,
        "user_id": test_user_id,
        "exp": datetime.utcnow() - timedelta(hours=1)  # Expired
    }
    token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")
    return token


@pytest.fixture
def invalid_jwt_token():
    """Generate an invalid JWT token for testing."""
    return "invalid.jwt.token"


@pytest.fixture(scope="function")
def setup_test_user_sync(test_user_id):
    """Create a test user in the database before each test (synchronous version)."""
    import asyncio
    from app.database import async_engine
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker
    from app.models.user import User
    from sqlmodel import select

    async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

    async def create_user():
        async with async_session() as session:
            # Check if user exists
            stmt = select(User).where(User.id == int(test_user_id))
            result = await session.execute(stmt)
            existing_user = result.scalar_one_or_none()

            if not existing_user:
                # Create test user
                test_user = User(id=int(test_user_id), email=f"test{test_user_id}@example.com")
                session.add(test_user)
                await session.commit()

    async def delete_user():
        async with async_session() as session:
            stmt = select(User).where(User.id == int(test_user_id))
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            if user:
                await session.delete(user)
                await session.commit()

    # Create user before test
    asyncio.run(create_user())

    yield

    # Cleanup: delete test user after test
    asyncio.run(delete_user())
