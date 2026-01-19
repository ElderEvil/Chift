"""
Authentication utilities for password hashing and JWT token management.

This module provides core authentication functions without FastAPI dependencies,
making it reusable across different contexts.
"""

from datetime import UTC, datetime, timedelta
import hashlib

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.schemas.auth import TokenData

# Password hashing context
# Note: bcrypt has a 72-byte limit. We handle this by pre-hashing long passwords
# with SHA-256 before passing them to bcrypt (see _prepare_password function).
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def _prepare_password(password: str) -> str:
    """
    Prepare password for bcrypt hashing.

    Bcrypt has a 72-byte limit. For passwords exceeding this limit,
    we first hash with SHA-256 to create a fixed-length digest, then
    bcrypt the digest. This is cryptographically sound and ensures
    no password truncation occurs.

    Args:
        password: The plain text password

    Returns:
        Password ready for bcrypt (either original or SHA-256 digest)
    """
    password_bytes = password.encode("utf-8")

    # If password is >72 bytes, pre-hash with SHA-256
    if len(password_bytes) > 72:
        # SHA-256 produces 64 hex characters (32 bytes), well under 72 byte limit
        return hashlib.sha256(password_bytes).hexdigest()

    return password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a bcrypt hash.

    Handles passwords >72 bytes by pre-hashing with SHA-256.
    This is safe and ensures consistent behavior with get_password_hash().

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hash to verify against

    Returns:
        True if password matches, False otherwise
    """
    prepared_password = _prepare_password(plain_password)
    return pwd_context.verify(prepared_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generate a bcrypt hash for a password.

    Handles passwords >72 bytes by pre-hashing with SHA-256.
    This ensures no password is truncated and all passwords can be hashed.

    Args:
        password: Plain text password to hash

    Returns:
        Bcrypt hash string
    """
    prepared_password = _prepare_password(password)
    return pwd_context.hash(prepared_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> TokenData:
    """
    Decode and validate a JWT access token.

    Args:
        token: JWT token string to decode

    Returns:
        TokenData with username from token payload

    Raises:
        jose.JWTError: If token is invalid or expired
    """
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    username: str | None = payload.get("sub")
    if username is None:
        raise ValueError("Token missing 'sub' claim")
    return TokenData(username=username)
