from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.core.scheduler import scheduler
from app.routers import auth, contacts, invoices

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting up Chift API...")

    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

    # Start the sync scheduler
    try:
        scheduler.start()
        logger.info("Sync scheduler started")
    except Exception as e:
        logger.error(f"Scheduler startup failed: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Chift API...")
    try:
        scheduler.stop()
        logger.info("Sync scheduler stopped")
    except Exception as e:
        logger.error(f"Scheduler shutdown failed: {e}")


# Create FastAPI app
app = FastAPI(
    title="Chift - Odoo Integration API",
    description="API for syncing and retrieving contacts and invoices from Odoo",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(contacts.router, prefix=settings.api_v1_prefix)
app.include_router(invoices.router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Chift API",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "authentication": f"{settings.api_v1_prefix}/auth",
            "contacts": f"{settings.api_v1_prefix}/contacts",
            "invoices": f"{settings.api_v1_prefix}/invoices",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "scheduler_running": scheduler.is_running,
    }
