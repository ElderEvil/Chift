from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.invoice import Invoice


class InvoiceRepository:
    """Repository for Invoice database operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self, skip: int = 0, limit: int = 100, include_deleted: bool = False
    ) -> list[Invoice]:
        """Get all invoices with pagination"""
        query = select(Invoice)
        if not include_deleted:
            query = query.where(not Invoice.is_deleted)
        query = query.offset(skip).limit(limit)
        return list(self.db.scalars(query).all())

    def get_by_id(self, invoice_id: int) -> Invoice | None:
        """Get invoice by internal ID"""
        return self.db.get(Invoice, invoice_id)

    def get_by_odoo_id(self, odoo_id: int) -> Invoice | None:
        """Get invoice by Odoo ID"""
        query = select(Invoice).where(Invoice.odoo_id == odoo_id)
        return self.db.scalar(query)

    def create(self, invoice_data: dict) -> Invoice:
        """Create a new invoice"""
        invoice = Invoice(**invoice_data)
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def update(self, invoice: Invoice, update_data: dict) -> Invoice:
        """Update an existing invoice"""
        for key, value in update_data.items():
            if hasattr(invoice, key):
                setattr(invoice, key, value)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def soft_delete(self, invoice: Invoice) -> Invoice:
        """Soft delete an invoice (mark as deleted)"""
        invoice.is_deleted = True
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def delete(self, invoice: Invoice) -> None:
        """Hard delete an invoice (remove from database)"""
        self.db.delete(invoice)
        self.db.commit()

    def get_all_odoo_ids(self) -> list[int]:
        """Get all Odoo IDs from invoices in the database"""
        query = select(Invoice.odoo_id).where(not Invoice.is_deleted)
        return list(self.db.scalars(query).all())

    def count(self, include_deleted: bool = False) -> int:
        """Count total invoices"""
        query = select(Invoice)
        if not include_deleted:
            query = query.where(not Invoice.is_deleted)
        return len(list(self.db.scalars(query).all()))
