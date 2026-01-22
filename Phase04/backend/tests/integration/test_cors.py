"""
Integration tests for CORS middleware.

Tests:
- CORS preflight (OPTIONS) request
- CORS actual request with credentials
- CORS rejects wildcard origins in production mode
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.config import settings

client = TestClient(app)


def test_cors_preflight_request():
    """Test CORS preflight (OPTIONS) request is handled correctly."""
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,Authorization",
        }
    )

    # Preflight should return 200 OK
    assert response.status_code == 200

    # Check CORS headers
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "access-control-allow-credentials" in response.headers
    assert response.headers["access-control-allow-credentials"] == "true"


def test_cors_actual_request_with_credentials():
    """Test CORS actual request with credentials is allowed."""
    response = client.get(
        "/",
        headers={
            "Origin": "http://localhost:3000",
        }
    )

    # Actual request should succeed
    assert response.status_code == 200

    # Check CORS headers
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "access-control-allow-credentials" in response.headers
    assert response.headers["access-control-allow-credentials"] == "true"


def test_cors_rejects_unauthorized_origin():
    """Test CORS rejects requests from unauthorized origins."""
    response = client.get(
        "/",
        headers={
            "Origin": "http://malicious-site.com",
        }
    )

    # Request may succeed but CORS headers should not allow the origin
    # FastAPI CORS middleware will not set access-control-allow-origin for unauthorized origins
    if "access-control-allow-origin" in response.headers:
        assert response.headers["access-control-allow-origin"] != "http://malicious-site.com"


def test_cors_configuration_in_development():
    """Test CORS configuration in development mode."""
    with patch("app.middleware.cors.settings.environment", "development"):
        with patch("app.middleware.cors.settings.frontend_url", "http://localhost:3000"):
            from app.middleware.cors import configure_cors
            from fastapi import FastAPI

            test_app = FastAPI()
            allowed_origins = configure_cors(test_app)

            # Development should allow localhost:3000
            assert "http://localhost:3000" in allowed_origins


def test_cors_configuration_in_production():
    """Test CORS configuration in production mode (no wildcard)."""
    with patch("app.middleware.cors.settings.environment", "production"):
        with patch("app.middleware.cors.settings.frontend_url", "https://my-app.vercel.app"):
            from app.middleware.cors import configure_cors
            from fastapi import FastAPI

            test_app = FastAPI()
            allowed_origins = configure_cors(test_app)

            # Production should only allow the specific frontend URL
            assert allowed_origins == ["https://my-app.vercel.app"]

            # Must not contain wildcards
            assert "*" not in allowed_origins


def test_cors_allows_specific_methods():
    """Test CORS allows only specific HTTP methods."""
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        }
    )

    assert response.status_code == 200

    # Check allowed methods
    if "access-control-allow-methods" in response.headers:
        allowed_methods = response.headers["access-control-allow-methods"]
        assert "GET" in allowed_methods or "POST" in allowed_methods


def test_cors_allows_specific_headers():
    """Test CORS allows specific headers (Content-Type, Authorization)."""
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,Authorization",
        }
    )

    assert response.status_code == 200

    # Check allowed headers
    if "access-control-allow-headers" in response.headers:
        allowed_headers = response.headers["access-control-allow-headers"].lower()
        assert "content-type" in allowed_headers or "authorization" in allowed_headers
