from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.deal_repository import DealRepository
from src.repositories.organization_member_repository import OrganizationMemberRepository


cache = {}


class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.deal_repo = DealRepository(session)
        self.member_repo = OrganizationMemberRepository(session)

    async def get_deals_summary(self, organization_id: UUID, user_id: UUID) -> dict:
        member = await self.member_repo.get_by_org_and_user(organization_id, user_id)
        if not member:
            raise ValueError("access denied")
        cache_key = f"deals_summary_{organization_id}"
        if cache_key in cache:
            return cache[cache_key]
        summary = await self.deal_repo.get_summary(organization_id)
        cache[cache_key] = summary
        return summary

    async def get_deals_funnel(self, organization_id: UUID, user_id: UUID) -> dict:
        member = await self.member_repo.get_by_org_and_user(organization_id, user_id)
        if not member:
            raise ValueError("access denied")
        cache_key = f"deals_funnel_{organization_id}"
        if cache_key in cache:
            return cache[cache_key]
        funnel = await self.deal_repo.get_funnel(organization_id)
        cache[cache_key] = funnel
        return funnel

