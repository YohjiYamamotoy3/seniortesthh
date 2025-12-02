from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.repositories.activity_repository import ActivityRepository
from src.api.dependencies import get_current_user, get_organization_member
from src.api.v1.schemas import ActivityResponse
from src.models.user import User
from src.models.organization_member import OrganizationMember

router = APIRouter()


@router.get("/activities", response_model=List[ActivityResponse])
async def list_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    deal_id: UUID = Query(None),
    current_user: User = Depends(get_current_user),
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    activity_repo = ActivityRepository(db)
    if deal_id:
        activities = await activity_repo.get_by_deal(member.organization_id, deal_id)
    else:
        activities = await activity_repo.get_by_organization(member.organization_id, skip, limit)
    return activities

