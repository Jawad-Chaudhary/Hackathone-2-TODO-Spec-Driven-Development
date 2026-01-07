# Test configuration and fixtures

import pytest
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta

from app.main import app
from app.config import settings


@pytest.fixture(scope="function")
def client():
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_user_id():
    """Return a test user ID."""
    return "test-user-123"


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
