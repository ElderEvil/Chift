import logging
from typing import Any
import xmlrpc.client

from app.core.config import settings

logger = logging.getLogger(__name__)


class OdooClient:
    """Client for interacting with Odoo XML-RPC API"""

    def __init__(self):
        self.url = settings.odoo_url
        self.db = settings.odoo_db
        self.username = settings.odoo_username
        self.password = settings.odoo_password
        self.uid: int | None = None
        self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

    def authenticate(self) -> int:
        """
        Authenticate with Odoo and return user ID.
        Raises exception if authentication fails.
        """
        try:
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            if not self.uid:
                raise Exception("Authentication failed: Invalid credentials")
            logger.info(f"Successfully authenticated with Odoo. User ID: {self.uid}")
            return self.uid
        except Exception as e:
            logger.error(f"Odoo authentication error: {e}")
            raise

    def _execute_kw(self, model: str, method: str, args: list, kwargs: dict | None = None) -> Any:
        """
        Execute a method on an Odoo model.
        Automatically authenticates if not already authenticated.
        """
        if not self.uid:
            self.authenticate()

        if kwargs is None:
            kwargs = {}

        try:
            return self.models.execute_kw(
                self.db, self.uid, self.password, model, method, args, kwargs
            )
        except Exception as e:
            logger.error(f"Error executing {method} on {model}: {e}")
            raise

    def fetch_contacts(
        self, limit: int | None = None, offset: int = 0, domain: list | None = None
    ) -> list[dict[str, Any]]:
        """
        Fetch contacts (partners) from Odoo.

        Args:
            limit: Maximum number of records to fetch
            offset: Number of records to skip
            domain: Odoo domain filter (e.g., [['is_company', '=', False]])

        Returns:
            List of contact dictionaries with fields: id, name, email, phone, etc.
        """
        if domain is None:
            domain = []

        fields = [
            "id",
            "name",
            "email",
            "phone",
            "street",
            "city",
            "country_id",
            "write_date",
        ]

        kwargs = {"fields": fields, "offset": offset}
        if limit:
            kwargs["limit"] = limit

        try:
            contacts = self._execute_kw("res.partner", "search_read", [domain], kwargs)
            logger.info(f"Fetched {len(contacts)} contacts from Odoo")
            return contacts
        except Exception as e:
            logger.error(f"Error fetching contacts: {e}")
            raise

    def fetch_contact_by_id(self, odoo_id: int) -> dict[str, Any] | None:
        """
        Fetch a single contact by Odoo ID.

        Args:
            odoo_id: Odoo partner ID

        Returns:
            Contact dictionary or None if not found
        """
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "street",
            "city",
            "country_id",
            "write_date",
        ]

        try:
            contacts = self._execute_kw(
                "res.partner",
                "search_read",
                [[["id", "=", odoo_id]]],
                {"fields": fields},
            )
            return contacts[0] if contacts else None
        except Exception as e:
            logger.error(f"Error fetching contact {odoo_id}: {e}")
            return None

    def fetch_invoices(
        self, limit: int | None = None, offset: int = 0, domain: list | None = None
    ) -> list[dict[str, Any]]:
        """
        Fetch invoices from Odoo.

        Args:
            limit: Maximum number of records to fetch
            offset: Number of records to skip
            domain: Odoo domain filter

        Returns:
            List of invoice dictionaries
        """
        if domain is None:
            domain = []

        fields = [
            "id",
            "name",  # invoice number
            "partner_id",
            "invoice_date",
            "invoice_date_due",
            "amount_total",
            "state",
            "write_date",
        ]

        kwargs = {"fields": fields, "offset": offset}
        if limit:
            kwargs["limit"] = limit

        try:
            invoices = self._execute_kw("account.move", "search_read", [domain], kwargs)
            logger.info(f"Fetched {len(invoices)} invoices from Odoo")
            return invoices
        except Exception as e:
            logger.error(f"Error fetching invoices: {e}")
            raise

    def fetch_invoice_by_id(self, odoo_id: int) -> dict[str, Any] | None:
        """
        Fetch a single invoice by Odoo ID.

        Args:
            odoo_id: Odoo invoice ID

        Returns:
            Invoice dictionary or None if not found
        """
        fields = [
            "id",
            "name",
            "partner_id",
            "invoice_date",
            "invoice_date_due",
            "amount_total",
            "state",
            "write_date",
        ]

        try:
            invoices = self._execute_kw(
                "account.move",
                "search_read",
                [[["id", "=", odoo_id]]],
                {"fields": fields},
            )
            return invoices[0] if invoices else None
        except Exception as e:
            logger.error(f"Error fetching invoice {odoo_id}: {e}")
            return None

    def get_all_contact_ids(self) -> list[int]:
        """
        Get all contact IDs from Odoo.
        Useful for detecting deletions.
        """
        try:
            ids = self._execute_kw("res.partner", "search", [[]])
            logger.info(f"Found {len(ids)} total contacts in Odoo")
            return ids
        except Exception as e:
            logger.error(f"Error fetching contact IDs: {e}")
            raise

    def get_all_invoice_ids(self) -> list[int]:
        """
        Get all invoice IDs from Odoo.
        Useful for detecting deletions.
        """
        try:
            ids = self._execute_kw("account.move", "search", [[]])
            logger.info(f"Found {len(ids)} total invoices in Odoo")
            return ids
        except Exception as e:
            logger.error(f"Error fetching invoice IDs: {e}")
            raise
