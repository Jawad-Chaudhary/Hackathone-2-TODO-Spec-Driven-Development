# [Task T016] Authentication dependency for extracting user_id from JWT

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.middleware.auth import verify_jwt_token


# HTTP Bearer security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    FastAPI dependency to extract and validate user_id from JWT token.

    Args:
        credentials: HTTP Authorization header with Bearer token

    Returns:
        user_id: String identifier of the authenticated user

    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    token = credentials.credentials
    payload = verify_jwt_token(token)

    # Extract user_id from JWT payload
    user_id = payload.get("sub") or payload.get("user_id") or payload.get("id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not contain user identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id
