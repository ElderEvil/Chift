from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class ContactBase(BaseModel):
    """Base schema for Contact"""

    name: str
    email: EmailStr | None = None
    phone: str | None = None
    street: str | None = None
    city: str | None = None
    country: str | None = None


class ContactResponse(ContactBase):
    """Schema for Contact response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    odoo_id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class ContactListResponse(BaseModel):
    """Schema for paginated contacts list"""

    total: int
    skip: int
    limit: int
    contacts: list[ContactResponse]
