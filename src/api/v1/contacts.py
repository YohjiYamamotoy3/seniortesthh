from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.services.contact_service import ContactService
from src.api.dependencies import get_current_user, get_organization_member
from src.api.v1.schemas import ContactCreate, ContactUpdate, ContactResponse
from src.models.user import User
from src.models.organization_member import OrganizationMember

router = APIRouter()


@router.post("/contacts", response_model=ContactResponse, status_code=201)
async def create_contact(
    contact_data: ContactCreate,
    current_user: User = Depends(get_current_user),
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    contact_service = ContactService(db)
    try:
        contact = await contact_service.create_contact(
            member.organization_id,
            current_user.id,
            contact_data.name,
            contact_data.email,
            contact_data.phone,
            contact_data.company,
            contact_data.notes
        )
        return contact
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/contacts", response_model=List[ContactResponse])
async def list_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    contact_service = ContactService(db)
    try:
        contacts = await contact_service.list_contacts(
            member.organization_id,
            current_user.id,
            skip,
            limit
        )
        return contacts
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: UUID,
    current_user: User = Depends(get_current_user),
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(
        member.organization_id,
        contact_id,
        current_user.id
    )
    if not contact:
        raise HTTPException(status_code=404, detail="contact not found")
    return contact


@router.patch("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: UUID,
    contact_data: ContactUpdate,
    current_user: User = Depends(get_current_user),
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    contact_service = ContactService(db)
    update_data = contact_data.model_dump(exclude_unset=True)
    try:
        contact = await contact_service.update_contact(
            member.organization_id,
            contact_id,
            current_user.id,
            **update_data
        )
        if not contact:
            raise HTTPException(status_code=404, detail="contact not found")
        return contact
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/contacts/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: UUID,
    current_user: User = Depends(get_current_user),
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    contact_service = ContactService(db)
    try:
        result = await contact_service.delete_contact(
            member.organization_id,
            contact_id,
            current_user.id
        )
        if not result:
            raise HTTPException(status_code=404, detail="contact not found")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

