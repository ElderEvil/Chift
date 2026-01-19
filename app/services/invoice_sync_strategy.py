from typing import Any

from app.repositories.invoice_repository import InvoiceRepository
from app.services.sync_strategy import SyncStrategy


class InvoiceSyncStrategy(SyncStrategy):
    """Strategy for syncing invoices from Odoo"""

    def fetch_odoo_data(self) -> list[dict[str, Any]]:
        """Fetch invoices from Odoo (customer invoices only)"""
        domain = [["move_type", "=", "out_invoice"]]
        return self.odoo_client.fetch_invoices(domain=domain)

    def get_repository(self):
        """Get invoice repository"""
        return InvoiceRepository(self.db)

    def map_odoo_to_db(self, odoo_invoice: dict[str, Any]) -> dict[str, Any]:
        """Map Odoo invoice data to database schema"""
        partner_id = None
        partner_name = None
        if odoo_invoice.get("partner_id"):
            # partner_id is a tuple (id, name) or False
            if isinstance(odoo_invoice["partner_id"], (list, tuple)):
                partner_id = odoo_invoice["partner_id"][0]
                partner_name = odoo_invoice["partner_id"][1]

        # Odoo returns False for empty fields - draft invoices often don't have numbers yet
        invoice_number = odoo_invoice.get("name")
        if not invoice_number or invoice_number is False:
            invoice_number = f"DRAFT-{odoo_invoice['id']}"
            self.logger.warning(
                f"Invoice {odoo_invoice['id']} has no invoice number, using placeholder: {invoice_number}"
            )

        invoice_date = odoo_invoice.get("invoice_date")
        if invoice_date is False:
            invoice_date = None
            self.logger.debug(
                f"Invoice {odoo_invoice['id']} has no invoice_date (likely draft state)"
            )

        due_date = odoo_invoice.get("invoice_date_due")
        if due_date is False:
            due_date = None
            self.logger.debug(
                f"Invoice {odoo_invoice['id']} has no due_date"
            )

        return {
            "odoo_id": odoo_invoice["id"],
            "invoice_number": invoice_number,
            "partner_id": partner_id,
            "partner_name": partner_name,
            "invoice_date": invoice_date,
            "due_date": due_date,
            "amount_total": odoo_invoice.get("amount_total", 0),
            "state": odoo_invoice.get("state", "draft"),
            "is_deleted": False,
        }

    def get_entity_name(self) -> str:
        """Get entity name for logging"""
        return "invoice"
