import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.services.sync_orchestrator import SyncOrchestrator

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def sync_job():
    """Job function to sync contacts and invoices from Odoo"""
    logger.info("=" * 60)
    logger.info("Starting scheduled sync job...")

    sync_orchestrator = None
    try:
        sync_orchestrator = SyncOrchestrator()
        results = sync_orchestrator.sync_all()

        logger.info("Sync job completed successfully")

        contacts = results.results.get("contacts")
        if contacts:
            logger.info(
                f"Contacts - Inserted: {contacts.inserted}, "
                f"Updated: {contacts.updated}, "
                f"Deleted: {contacts.deleted}, "
                f"Errors: {contacts.errors}"
            )

        invoices = results.results.get("invoices")
        if invoices:
            logger.info(
                f"Invoices - Inserted: {invoices.inserted}, "
                f"Updated: {invoices.updated}, "
                f"Deleted: {invoices.deleted}, "
                f"Errors: {invoices.errors}"
            )

    except Exception as e:
        logger.error(f"Sync job failed: {e}", exc_info=True)
    finally:
        if sync_orchestrator:
            sync_orchestrator.close()

    logger.info("=" * 60)


class SyncScheduler:
    """Scheduler for periodic Odoo synchronization"""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False

    def start(self):
        """Start the scheduler with configured interval"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return

        interval_minutes = settings.sync_interval_minutes
        logger.info(f"Starting scheduler with {interval_minutes} minute interval")

        # Schedule the job to run every X minutes
        self.scheduler.add_job(
            sync_job,
            trigger=CronTrigger(minute=f"*/{interval_minutes}"),
            id="odoo_sync_job",
            name="Odoo Sync Job",
            replace_existing=True,
        )

        self.scheduler.start()
        self.is_running = True
        logger.info("Scheduler started successfully")

        # Run the sync immediately on startup
        logger.info("Running initial sync...")
        sync_job()

    def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return

        self.scheduler.shutdown()
        self.is_running = False
        logger.info("Scheduler stopped")

    def run_manual_sync(self):
        """Run a manual sync outside of the schedule"""
        logger.info("Manual sync triggered")
        sync_job()


# Global scheduler instance
scheduler = SyncScheduler()
