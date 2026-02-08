# [Task T038] CORS middleware configuration with environment-based origins

from fastapi.middleware.cors import CORSMiddleware
from app.config import settings


def configure_cors(app):
    """
    Configure CORS middleware for the FastAPI application.

    Behavior:
    - Development: Allows localhost:3000 and FRONTEND_URL
    - Production: Only allows explicitly configured FRONTEND_URL
    - Always allows credentials (required for JWT tokens)
    - Restricted methods: GET, POST, PUT, DELETE, OPTIONS
    - Restricted headers: Content-Type, Authorization

    Security:
    - NO wildcard (*) origins in production
    - Explicit origin whitelist from environment variables
    - Credentials support for authentication flows

    Args:
        app: FastAPI application instance
    """
    # Determine allowed origins based on environment
    if settings.environment == "development":
        # Development: Allow localhost and FRONTEND_URL
        allowed_origins = [
            "http://localhost:3000",
            settings.frontend_url,
        ]
        # Remove duplicates
        allowed_origins = list(set(allowed_origins))
    else:
        # Production: Only allow explicitly configured FRONTEND_URL
        allowed_origins = [settings.frontend_url]

    # Add CORS middleware with restricted configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,  # Required for JWT authentication
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    return allowed_origins  # Return for testing/verification
