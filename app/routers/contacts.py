from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.repositories.contact_repository import ContactRepository
from app.schemas.auth import User
from app.schemas.contact import ContactListResponse, ContactResponse

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("", response_model=ContactListResponse)
async def get_contacts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    include_deleted: bool = Query(False, description="Include soft-deleted contacts"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of contacts with pagination.

    **Authentication required**: Include JWT token in Authorization header.

    Parameters:
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (1-1000)
    - **include_deleted**: Include soft-deleted contacts in results
    """
    repo = ContactRepository(db)
    contacts = repo.get_all(skip=skip, limit=limit, include_deleted=include_deleted)
    total = repo.count(include_deleted=include_deleted)

    return ContactListResponse(
        total=total,
        skip=skip,
        limit=limit,
        contacts=contacts,
    )


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve a single contact by ID.

    **Authentication required**: Include JWT token in Authorization header.

    Parameters:
    - **contact_id**: Internal database ID of the contact
    """
    repo = ContactRepository(db)
    contact = repo.get_by_id(contact_id)

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found",
        )

    return contact
