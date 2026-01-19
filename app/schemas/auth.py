"""
Pydantic schemas for authentication endpoints.

This module contains request/response models for authentication operations.
"""

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """JWT token response model"""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """JWT token payload data"""

    username: str | None = None


class UserBase(BaseModel):
    """Base user model"""

    username: str
    email: EmailStr


class UserCreate(UserBase):
    """User creation request model"""

    password: str


class UserResponse(UserBase):
    """User response model (without sensitive data)"""

    id: int
    disabled: bool

    model_config = {"from_attributes": True}


class User(BaseModel):
    """User model for authentication (used in dependencies)"""

    username: str
    email: str
    disabled: bool


class UserInDB(User):
    """User model as stored in database (includes hashed password)"""

    hashed_password: str
