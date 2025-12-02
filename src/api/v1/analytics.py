from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.services.analytics_service import AnalyticsService
from src.api.dependencies import get_current_user, get_organization_member
from src.api.v1.schemas import DealsSummaryResponse, DealsFunnelResponse
from src.models.user import User
from src.models.organization_member import OrganizationMember

router = APIRouter()


@router.get("/analytics/deals/summary", response_model=DealsSummaryResponse)
async def get_deals_summary(
    current_user: User = Depends(get_current_user),
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    analytics_service = AnalyticsService(db)
    try:
        summary = await analytics_service.get_deals_summary(member.organization_id, current_user.id)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/analytics/deals/funnel", response_model=DealsFunnelResponse)
async def get_deals_funnel(
    current_user: User = Depends(get_current_user),
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    analytics_service = AnalyticsService(db)
    try:
        funnel = await analytics_service.get_deals_funnel(member.organization_id, current_user.id)
        return funnel
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

