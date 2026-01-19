from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.repositories.invoice_repository import InvoiceRepository
from app.schemas.auth import User
from app.schemas.invoice import InvoiceListResponse, InvoiceResponse

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("", response_model=InvoiceListResponse)
async def get_invoices(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    include_deleted: bool = Query(False, description="Include soft-deleted invoices"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of invoices with pagination.

    **Authentication required**: Include JWT token in Authorization header.

    Parameters:
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (1-1000)
    - **include_deleted**: Include soft-deleted invoices in results
    """
    repo = InvoiceRepository(db)
    invoices = repo.get_all(skip=skip, limit=limit, include_deleted=include_deleted)
    total = repo.count(include_deleted=include_deleted)

    return InvoiceListResponse(
        total=total,
        skip=skip,
        limit=limit,
        invoices=invoices,
    )


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve a single invoice by ID.

    **Authentication required**: Include JWT token in Authorization header.

    Parameters:
    - **invoice_id**: Internal database ID of the invoice
    """
    repo = InvoiceRepository(db)
    invoice = repo.get_by_id(invoice_id)

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with ID {invoice_id} not found",
        )

    return invoice
