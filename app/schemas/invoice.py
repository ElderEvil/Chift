from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class InvoiceBase(BaseModel):
    """Base schema for Invoice"""

    invoice_number: str
    partner_id: int
    partner_name: str | None = None
    invoice_date: date | None = None
    due_date: date | None = None
    amount_total: Decimal
    state: str


class InvoiceResponse(InvoiceBase):
    """Schema for Invoice response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    odoo_id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class InvoiceListResponse(BaseModel):
    """Schema for paginated invoices list"""

    total: int
    skip: int
    limit: int
    invoices: list[InvoiceResponse]
