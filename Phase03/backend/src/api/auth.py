# [Task]: Authentication Implementation
# [From]: Phase II - Better Auth + JWT Integration

"""
Authentication API Routes

Implements signup and signin endpoints with JWT token generation.
Uses bcrypt for password hashing and python-jose for JWT tokens.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from pydantic import BaseModel, EmailStr, Field
import bcrypt
from jose import jwt
from datetime import datetime, timedelta
import os
from typing import Optional

from ..database.session import get_db_session
from ..models.user import User

# Router for authentication endpoints
router = APIRouter(
    prefix="/api/auth",
    tags=["authentication"],
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        409: {"description": "Conflict - User already exists"}
    }
)

# JWT configuration
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
if not BETTER_AUTH_SECRET:
    raise RuntimeError("BETTER_AUTH_SECRET environment variable is required")

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days


# Request/Response Models
class SignupRequest(BaseModel):
    """Signup request payload"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password (min 8 characters)")
    full_name: Optional[str] = Field(None, max_length=255, description="User's full name")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "full_name": "John Doe"
            }
        }


class SigninRequest(BaseModel):
    """Signin request payload"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }


class AuthResponse(BaseModel):
    """Authentication response with JWT token"""
    token: str = Field(..., description="JWT access token")
    user_id: str = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    full_name: Optional[str] = Field(None, description="User's full name")

    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "user_id": "1",
                "email": "user@example.com",
                "full_name": "John Doe"
            }
        }


# Helper functions
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    # Convert password to bytes and hash with bcrypt
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_jwt_token(user_id: int, email: str) -> str:
    """
    Create a JWT token for authenticated user.

    Args:
        user_id: User's database ID
        email: User's email address

    Returns:
        JWT token string
    """
    expiration = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)

    payload = {
        "sub": str(user_id),  # Standard JWT claim for user identifier
        "user_id": str(user_id),  # Additional claim for compatibility
        "email": email,
        "exp": expiration,
        "iat": datetime.utcnow()
    }

    token = jwt.encode(payload, BETTER_AUTH_SECRET, algorithm=JWT_ALGORITHM)
    return token


# API Endpoints
@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=201,
    summary="Create new user account",
    description="Register a new user with email and password. Returns JWT token for immediate authentication."
)
async def signup(
    request: SignupRequest,
    session: AsyncSession = Depends(get_db_session)
) -> AuthResponse:
    """
    Create a new user account and return JWT token.

    Steps:
    1. Validate email is not already registered
    2. Hash password using bcrypt
    3. Create user in database
    4. Generate JWT token
    5. Return token and user info

    Args:
        request: SignupRequest with email, password, and optional full_name
        session: Database session (dependency injected)

    Returns:
        AuthResponse with JWT token and user details

    Raises:
        HTTPException:
            - 409: Email already registered
            - 500: Database or internal error
    """
    try:
        # Check if user already exists
        stmt = select(User).where(User.email == request.email)
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=409,
                detail="Email already registered. Please use a different email or sign in."
            )

        # Hash password
        password_hash = hash_password(request.password)

        # Create new user
        new_user = User(
            email=request.email,
            password_hash=password_hash,
            full_name=request.full_name
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        # Generate JWT token
        token = create_jwt_token(new_user.id, new_user.email)

        # Return authentication response
        return AuthResponse(
            token=token,
            user_id=str(new_user.id),
            email=new_user.email,
            full_name=new_user.full_name
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log error and return generic message
        print(f"Error in signup endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create user account. Please try again."
        )


@router.post(
    "/signin",
    response_model=AuthResponse,
    summary="Sign in to existing account",
    description="Authenticate with email and password. Returns JWT token for API access."
)
async def signin(
    request: SigninRequest,
    session: AsyncSession = Depends(get_db_session)
) -> AuthResponse:
    """
    Authenticate existing user and return JWT token.

    Steps:
    1. Find user by email
    2. Verify password
    3. Generate JWT token
    4. Return token and user info

    Args:
        request: SigninRequest with email and password
        session: Database session (dependency injected)

    Returns:
        AuthResponse with JWT token and user details

    Raises:
        HTTPException:
            - 401: Invalid email or password
            - 500: Database or internal error
    """
    try:
        # Find user by email
        stmt = select(User).where(User.email == request.email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        # Verify user exists and password is correct
        if not user or not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password. Please check your credentials and try again."
            )

        # Generate JWT token
        token = create_jwt_token(user.id, user.email)

        # Return authentication response
        return AuthResponse(
            token=token,
            user_id=str(user.id),
            email=user.email,
            full_name=user.full_name
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log error and return generic message
        print(f"Error in signin endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to authenticate. Please try again."
        )
