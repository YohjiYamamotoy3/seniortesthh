from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.services.deal_service import DealService
from src.api.dependencies import get_current_user, get_organization_member
from src.api.v1.schemas import DealCreate, DealUpdate, DealResponse
from src.models.user import User
from src.models.organization_member import OrganizationMember

router = APIRouter()


@router.post("/deals", response_model=DealResponse, status_code=201)
async def create_deal(
    deal_data: DealCreate,
    current_user: User = Depends(get_current_user),
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    deal_service = DealService(db)
    try:
        deal = await deal_service.create_deal(
            member.organization_id,
            current_user.id,
            deal_data.contact_id,
            deal_data.title,
            deal_data.value,
            deal_data.stage,
            deal_data.notes
        )
        return deal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/deals", response_model=List[DealResponse])
async def list_deals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    deal_service = DealService(db)
    deals = await deal_service.list_deals(
        member.organization_id,
        current_user.id,
        skip,
        limit
    )
    return deals


@router.get("/deals/{deal_id}", response_model=DealResponse)
async def get_deal(
    deal_id: UUID,
    current_user: User = Depends(get_current_user),
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    deal_service = DealService(db)
    deal = await deal_service.get_deal(
        member.organization_id,
        deal_id,
        current_user.id
    )
    if not deal:
        raise HTTPException(status_code=404, detail="deal not found")
    return deal


@router.patch("/deals/{deal_id}", response_model=DealResponse)
async def update_deal(
    deal_id: UUID,
    deal_data: DealUpdate,
    current_user: User = Depends(get_current_user),
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    deal_service = DealService(db)
    update_data = deal_data.model_dump(exclude_unset=True)
    try:
        deal = await deal_service.update_deal(
            member.organization_id,
            deal_id,
            current_user.id,
            **update_data
        )
        if not deal:
            raise HTTPException(status_code=404, detail="deal not found")
        return deal
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/deals/{deal_id}/close", response_model=DealResponse)
async def close_deal(
    deal_id: UUID,
    current_user: User = Depends(get_current_user),
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    deal_service = DealService(db)
    try:
        deal = await deal_service.close_deal(
            member.organization_id,
            deal_id,
            current_user.id
        )
        if not deal:
            raise HTTPException(status_code=404, detail="deal not found")
        return deal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/deals/{deal_id}", status_code=204)
async def delete_deal(
    deal_id: UUID,
    current_user: User = Depends(get_current_user),
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    deal_service = DealService(db)
    try:
        result = await deal_service.delete_deal(
            member.organization_id,
            deal_id,
            current_user.id
        )
        if not result:
            raise HTTPException(status_code=404, detail="deal not found")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

