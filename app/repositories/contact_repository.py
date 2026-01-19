from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contact import Contact


class ContactRepository:
    """Repository for Contact database operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self, skip: int = 0, limit: int = 100, include_deleted: bool = False
    ) -> list[Contact]:
        """Get all contacts with pagination"""
        query = select(Contact)
        if not include_deleted:
            query = query.where(not Contact.is_deleted)
        query = query.offset(skip).limit(limit)
        return list(self.db.scalars(query).all())

    def get_by_id(self, contact_id: int) -> Contact | None:
        """Get contact by internal ID"""
        return self.db.get(Contact, contact_id)

    def get_by_odoo_id(self, odoo_id: int) -> Contact | None:
        """Get contact by Odoo ID"""
        query = select(Contact).where(Contact.odoo_id == odoo_id)
        return self.db.scalar(query)

    def create(self, contact_data: dict) -> Contact:
        """Create a new contact"""
        contact = Contact(**contact_data)
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def update(self, contact: Contact, update_data: dict) -> Contact:
        """Update an existing contact"""
        for key, value in update_data.items():
            if hasattr(contact, key):
                setattr(contact, key, value)
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def soft_delete(self, contact: Contact) -> Contact:
        """Soft delete a contact (mark as deleted)"""
        contact.is_deleted = True
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def delete(self, contact: Contact) -> None:
        """Hard delete a contact (remove from database)"""
        self.db.delete(contact)
        self.db.commit()

    def get_all_odoo_ids(self) -> list[int]:
        """Get all Odoo IDs from contacts in the database"""
        query = select(Contact.odoo_id).where(not Contact.is_deleted)
        return list(self.db.scalars(query).all())

    def count(self, include_deleted: bool = False) -> int:
        """Count total contacts"""
        query = select(Contact)
        if not include_deleted:
            query = query.where(not Contact.is_deleted)
        return len(list(self.db.scalars(query).all()))
