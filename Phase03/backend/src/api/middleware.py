# [Task]: T-024
# [From]: specs/001-ai-todo-chatbot/tasks.md

"""
JWT Authentication Middleware

Provides JWT token verification for securing API endpoints.
Uses BETTER_AUTH_SECRET from environment for token validation.
"""

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
from typing import Dict

# Security scheme for OpenAPI documentation
security = HTTPBearer()

# Get JWT secret from environment
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

if not BETTER_AUTH_SECRET:
    raise RuntimeError(
        "BETTER_AUTH_SECRET environment variable is required. "
        "Generate one with: openssl rand -hex 32"
    )


async def verify_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, str]:
    """
    Verify JWT token and extract user_id from payload.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        Dict containing user_id and other payload claims

    Raises:
        HTTPException: 401 if token is invalid, expired, or missing user_id

    Example:
        @app.get("/api/{user_id}/resource")
        async def endpoint(
            user_id: str,
            token_payload: dict = Depends(verify_jwt)
        ):
            if user_id != token_payload.get("user_id"):
                raise HTTPException(status_code=403, detail="User ID mismatch")
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization header"
        )

    token = credentials.credentials

    # DEVELOPMENT MODE: Allow mock token for testing without Better Auth setup
    # WARNING: This bypasses all JWT security checks. Never deploy to production with this enabled.
    if token == "mock-jwt-token-for-development":
        return {
            "user_id": "demo-user",
            "sub": "demo-user"
        }

    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )

        # Extract user_id from token (try both 'sub' and 'user_id' claims)
        user_id = payload.get("sub") or payload.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload: missing user identifier"
            )

        # Return full payload with normalized user_id
        return {
            "user_id": user_id,
            **payload
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Token verification failed: {str(e)}"
        )
