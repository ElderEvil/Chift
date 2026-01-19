"""
Pydantic schemas for request/response validation.

This module exports all schemas for easier imports.
"""

from app.schemas.auth import Token, TokenData, User, UserBase, UserCreate, UserInDB, UserResponse
from app.schemas.contact import ContactBase, ContactListResponse, ContactResponse
from app.schemas.invoice import InvoiceBase, InvoiceListResponse, InvoiceResponse
from app.schemas.sync import EntitySyncResult, SyncResult

__all__ = [
    # Contact schemas
    "ContactBase",
    "ContactListResponse",
    "ContactResponse",
    # Sync schemas
    "EntitySyncResult",
    # Invoice schemas
    "InvoiceBase",
    "InvoiceListResponse",
    "InvoiceResponse",
    "SyncResult",
    # Auth schemas
    "Token",
    "TokenData",
    "User",
    "UserBase",
    "UserCreate",
    "UserInDB",
    "UserResponse",
]
