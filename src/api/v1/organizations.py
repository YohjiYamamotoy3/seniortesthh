from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.services.organization_service import OrganizationService
from src.api.dependencies import get_current_user, get_organization_id, get_organization_member
from src.api.v1.schemas import OrganizationCreate, OrganizationResponse, MemberAdd, MemberResponse
from src.models.user import User
from src.models.organization_member import OrganizationMember

router = APIRouter()


@router.post("/organizations", response_model=OrganizationResponse, status_code=201)
async def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_service = OrganizationService(db)
    try:
        org = await org_service.create_organization(org_data.name, current_user.id)
        return org
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/organizations/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: str,
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    from uuid import UUID
    org_service = OrganizationService(db)
    org = await org_service.get_organization(UUID(organization_id))
    if not org:
        raise HTTPException(status_code=404, detail="organization not found")
    return org


@router.post("/organizations/{organization_id}/members", response_model=MemberResponse, status_code=201)
async def add_member(
    organization_id: str,
    member_data: MemberAdd,
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    from uuid import UUID
    org_service = OrganizationService(db)
    try:
        new_member = await org_service.add_member(
            UUID(organization_id),
            member_data.user_id,
            member_data.role,
            member.user_id
        )
        return new_member
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/organizations/{organization_id}/members", response_model=List[MemberResponse])
async def list_members(
    organization_id: str,
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    from uuid import UUID
    org_service = OrganizationService(db)
    members = await org_service.get_members(UUID(organization_id))
    return members

