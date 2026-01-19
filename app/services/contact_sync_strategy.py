from typing import Any

from app.repositories.contact_repository import ContactRepository
from app.services.sync_strategy import SyncStrategy


class ContactSyncStrategy(SyncStrategy):
    """Strategy for syncing contacts from Odoo"""

    def fetch_odoo_data(self) -> list[dict[str, Any]]:
        """Fetch contacts from Odoo"""
        return self.odoo_client.fetch_contacts()

    def get_repository(self):
        """Get contact repository"""
        return ContactRepository(self.db)

    def map_odoo_to_db(self, odoo_contact: dict[str, Any]) -> dict[str, Any]:
        """Map Odoo contact data to database schema"""
        country_name = None
        if odoo_contact.get("country_id"):
            # country_id is a tuple (id, name) or False
            country_name = (
                odoo_contact["country_id"][1]
                if isinstance(odoo_contact["country_id"], (list, tuple))
                else None
            )

        return {
            "odoo_id": odoo_contact["id"],
            "name": odoo_contact.get("name", ""),
            "email": odoo_contact.get("email") or None,
            "phone": odoo_contact.get("phone") or None,
            "street": odoo_contact.get("street") or None,
            "city": odoo_contact.get("city") or None,
            "country": country_name,
            "is_deleted": False,
        }

    def get_entity_name(self) -> str:
        """Get entity name for logging"""
        return "contact"
