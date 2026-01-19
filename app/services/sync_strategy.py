from abc import ABC, abstractmethod
import logging
import time
from typing import TYPE_CHECKING, Any

from sqlalchemy.orm import Session

from app.schemas.sync import EntitySyncResult, SyncResult

if TYPE_CHECKING:
    from app.repositories.contact_repository import ContactRepository
    from app.repositories.invoice_repository import InvoiceRepository

logger = logging.getLogger(__name__)


class SyncStrategy(ABC):
    """Abstract base class for sync strategies"""

    def __init__(self, db: Session, odoo_client):
        self.db = db
        self.odoo_client = odoo_client
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def fetch_odoo_data(self) -> list[dict[str, Any]]:
        """Fetch data from Odoo"""

    @abstractmethod
    def get_repository(self) -> "ContactRepository | InvoiceRepository":
        """Get the repository for this data type"""

    @abstractmethod
    def map_odoo_to_db(self, odoo_data: dict[str, Any]) -> dict[str, Any]:
        """Map Odoo data to database schema"""

    @abstractmethod
    def get_entity_name(self) -> str:
        """Get the name of the entity being synced"""

    def _upsert_item(
        self, odoo_item: dict[str, Any], repository: Any, result: SyncResult, entity_name: str
    ) -> None:
        """Process a single item (insert or update)"""
        db_data = self.map_odoo_to_db(odoo_item)
        existing = repository.get_by_odoo_id(odoo_item["id"])

        if existing:
            repository.update(existing, db_data)
            result.updated += 1
            self.logger.debug(f"Updated {entity_name}: {odoo_item.get('name', odoo_item['id'])}")
        else:
            repository.create(db_data)
            result.inserted += 1
            self.logger.debug(f"Inserted {entity_name}: {odoo_item.get('name', odoo_item['id'])}")

    def _process_upserts(
        self, odoo_data: list[dict[str, Any]], repository: Any, result: SyncResult, entity_name: str
    ) -> None:
        """Process all insert/update operations"""
        for odoo_item in odoo_data:
            try:
                self._upsert_item(odoo_item, repository, result, entity_name)
            except Exception as e:
                result.add_error(f"Error processing {entity_name} {odoo_item.get('id')}: {e}")

    def _process_soft_deletes(
        self, deleted_ids: set[int], repository: Any, result: SyncResult, entity_name: str
    ) -> None:
        """Process all soft delete operations"""
        for odoo_id in deleted_ids:
            try:
                item = repository.get_by_odoo_id(odoo_id)
                if item and not item.is_deleted:
                    repository.soft_delete(item)
                    result.deleted += 1
                    self.logger.debug(f"Soft deleted {entity_name}: {item}")
            except Exception as e:
                result.add_error(f"Error deleting {entity_name} {odoo_id}: {e}")

    def sync(self) -> EntitySyncResult:
        """Execute the sync process using the strategy pattern"""
        start_time = time.time()
        result = SyncResult()
        entity_name = self.get_entity_name()

        try:
            self.logger.info(f"Starting {entity_name} sync...")

            # Fetch data from Odoo
            odoo_data = self.fetch_odoo_data()
            odoo_ids = {item["id"] for item in odoo_data}

            # Get repository and existing IDs
            repository = self.get_repository()
            if repository is None:
                raise ValueError(f"Repository not found for {entity_name}")

            db_odoo_ids = set(repository.get_all_odoo_ids())

            # Process upserts and deletes
            self._process_upserts(odoo_data, repository, result, entity_name)
            deleted_ids = db_odoo_ids - odoo_ids
            self._process_soft_deletes(deleted_ids, repository, result, entity_name)

            duration = time.time() - start_time
            log_msg = f"{entity_name} sync completed in {duration:.2f}s: {result}"
            if result.error_details:
                log_msg += f" | Errors: {', '.join(result.error_details)}"
            self.logger.info(log_msg)

        except Exception as e:
            result.add_error(f"{entity_name} sync failed: {e}")
            self.logger.error(f"{entity_name} sync failed: {e}")
            raise

        duration = time.time() - start_time
        return EntitySyncResult(entity_name=entity_name, result=result, duration_seconds=duration)
