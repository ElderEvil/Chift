"""
FastAPI dependency functions for authentication and authorization.

This module provides FastAPI-specific dependencies that can be injected
into route handlers using Depends().
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.auth import decode_access_token, verify_password
from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth import User

# HTTP Bearer token security scheme
security = HTTPBearer()


def get_user(username: str, db: Session) -> User | None:
    """
    Retrieve a user by username from database.

    Args:
        username: Username to look up
        db: Database session

    Returns:
        User schema object if found, None otherwise
    """
    user_repo = UserRepository(db)
    user_model = user_repo.get_by_username(username)
    if not user_model:
        return None
    return User(username=user_model.username, email=user_model.email, disabled=user_model.disabled)


def authenticate_user(username: str, password: str, db: Session) -> User | None:
    """
    Authenticate a user by username and password.

    Args:
        username: Username to authenticate
        password: Plain text password
        db: Database session

    Returns:
        User schema object if authentication succeeds, None otherwise
    """
    user_repo = UserRepository(db)
    user_model = user_repo.get_by_username(username)
    if not user_model:
        return None

    if not verify_password(password, user_model.hashed_password):
        return None

    return User(username=user_model.username, email=user_model.email, disabled=user_model.disabled)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency to get current authenticated user from JWT token.

    This dependency:
    1. Extracts the Bearer token from the Authorization header
    2. Decodes and validates the JWT token
    3. Looks up the user from the database
    4. Returns the User object

    Args:
        credentials: HTTP Bearer credentials (injected by FastAPI)
        db: Database session (injected by FastAPI)

    Returns:
        Authenticated User object

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        token_data = decode_access_token(token)
    except (JWTError, ValueError):
        raise credentials_exception

    user = get_user(username=token_data.username, db=db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    FastAPI dependency to get current active (non-disabled) user.

    This dependency builds on get_current_user and adds an additional
    check to ensure the user account is not disabled.

    Args:
        current_user: Current user (injected by get_current_user dependency)

    Returns:
        Active User object

    Raises:
        HTTPException: 400 if user is disabled
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
