# [Task T015] JWT authentication middleware for validating Better Auth tokens

import jwt
from fastapi import HTTPException, status
from app.config import settings


def verify_jwt_token(token: str) -> dict:
    """
    Verify JWT token from Better Auth.

    Args:
        token: JWT token string from Authorization header

    Returns:
        Decoded JWT payload containing user_id and other claims

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Decode and verify JWT token
        # Skip audience/issuer verification as Better Auth may set these
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"],
            options={"verify_aud": False, "verify_iss": False},
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
