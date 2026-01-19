import logging
import time

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.schemas.sync import EntitySyncResult, FullSyncResult, SyncResult
from app.services.contact_sync_strategy import ContactSyncStrategy
from app.services.invoice_sync_strategy import InvoiceSyncStrategy
from app.services.odoo_client import OdooClient
from app.services.sync_strategy import SyncStrategy

logger = logging.getLogger(__name__)


class SyncOrchestrator:
    """
    Orchestrates sync operations using the Strategy pattern.
    Eliminates code duplication and provides better separation of concerns.
    """

    def __init__(self, db: Session | None = None):
        self.db = db or SessionLocal()
        self.odoo_client = OdooClient()
        self.strategies: dict[str, SyncStrategy] = {}

        # Register sync strategies
        self._register_strategies()

    def _register_strategies(self):
        """Register all available sync strategies"""
        self.strategies["contacts"] = ContactSyncStrategy(self.db, self.odoo_client)
        self.strategies["invoices"] = InvoiceSyncStrategy(self.db, self.odoo_client)

    def sync_entity(self, entity_name: str) -> EntitySyncResult:
        """
        Sync a single entity type using its registered strategy.

        Args:
            entity_name: Name of entity to sync ('contacts' or 'invoices')

        Returns:
            EntitySyncResult with operation statistics

        Raises:
            ValueError: If entity strategy not found
        """
        if entity_name not in self.strategies:
            raise ValueError(f"No sync strategy registered for entity: {entity_name}")

        strategy = self.strategies[entity_name]
        return strategy.sync()

    def sync_contacts(self) -> EntitySyncResult:
        """Sync contacts from Odoo to local database"""
        return self.sync_entity("contacts")

    def sync_contacts_dict(self) -> dict[str, int]:
        """Sync contacts and return as dict for backward compatibility"""
        result = self.sync_contacts()
        return result.result.model_dump()

    def sync_invoices(self) -> EntitySyncResult:
        """Sync invoices from Odoo to local database"""
        return self.sync_entity("invoices")

    def sync_invoices_dict(self) -> dict[str, int]:
        """Sync invoices and return as dict for backward compatibility"""
        result = self.sync_invoices()
        return result.result.model_dump()

    def sync_all(self) -> FullSyncResult:
        """
        Sync all registered entities.

        Returns:
            FullSyncResult with comprehensive results
        """
        start_time = time.time()
        logger.info("Starting full sync...")
        results = {}
        success_count = 0
        error_count = 0

        for entity_name in self.strategies:
            try:
                entity_result = self.sync_entity(entity_name)
                results[entity_name] = entity_result.result

                if entity_result.was_successful:
                    success_count += 1
                else:
                    error_count += 1

            except Exception as e:
                logger.error(f"Failed to sync {entity_name}: {e}")
                results[entity_name] = SyncResult()
                error_count += 1

        total_duration = time.time() - start_time
        full_result = FullSyncResult(
            results=results,
            total_duration_seconds=total_duration,
            success_count=success_count,
            error_count=error_count,
        )

        logger.info(
            f"Full sync completed in {total_duration:.2f}s: {full_result.total_inserted} inserted, {full_result.total_updated} updated, {full_result.total_deleted} deleted, {full_result.total_errors} errors"
        )
        return full_result

    def close(self):
        """Close the database session"""
        if self.db:
            self.db.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
