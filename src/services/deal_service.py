from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.deal_repository import DealRepository
from src.repositories.contact_repository import ContactRepository
from src.repositories.organization_member_repository import OrganizationMemberRepository
from src.repositories.activity_repository import ActivityRepository
from src.models.deal import Deal
from src.models.activity import Activity


class DealService:
    def __init__(self, session: AsyncSession):
        self.deal_repo = DealRepository(session)
        self.contact_repo = ContactRepository(session)
        self.member_repo = OrganizationMemberRepository(session)
        self.activity_repo = ActivityRepository(session)

    async def create_deal(self, organization_id: UUID, user_id: UUID, contact_id: UUID, title: str,
                          value: Optional[float] = None, stage: str = "new", notes: Optional[str] = None) -> Deal:
        member = await self.member_repo.get_by_org_and_user(organization_id, user_id)
        if not member:
            raise ValueError("access denied")
        contact = await self.contact_repo.get_by_id(contact_id)
        if not contact or contact.organization_id != organization_id:
            raise ValueError("contact not found")
        deal = Deal(
            organization_id=organization_id,
            contact_id=contact_id,
            title=title,
            value=value,
            stage=stage,
            notes=notes
        )
        deal = await self.deal_repo.create(deal)
        activity = Activity(
            organization_id=organization_id,
            user_id=user_id,
            deal_id=deal.id,
            type="deal_created",
            description=f"deal '{title}' created"
        )
        await self.activity_repo.create(activity)
        return deal

    async def get_deal(self, organization_id: UUID, deal_id: UUID, user_id: UUID) -> Optional[Deal]:
        member = await self.member_repo.get_by_org_and_user(organization_id, user_id)
        if not member:
            raise ValueError("access denied")
        deal = await self.deal_repo.get_by_id(deal_id)
        if deal and deal.organization_id != organization_id:
            return None
        return deal

    async def list_deals(self, organization_id: UUID, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Deal]:
        member = await self.member_repo.get_by_org_and_user(organization_id, user_id)
        if not member:
            raise ValueError("access denied")
        return await self.deal_repo.get_by_organization(organization_id, skip, limit)

    async def update_deal(self, organization_id: UUID, deal_id: UUID, user_id: UUID, **kwargs) -> Optional[Deal]:
        member = await self.member_repo.get_by_org_and_user(organization_id, user_id)
        if not member:
            raise ValueError("access denied")
        if member.role == "member":
            raise ValueError("insufficient permissions")
        deal = await self.deal_repo.get_by_id(deal_id)
        if not deal or deal.organization_id != organization_id:
            return None
        old_stage = deal.stage
        deal = await self.deal_repo.update(deal_id, **kwargs)
        if deal and "stage" in kwargs and kwargs["stage"] != old_stage:
            activity = Activity(
                organization_id=organization_id,
                user_id=user_id,
                deal_id=deal.id,
                type="deal_stage_changed",
                description=f"deal stage changed from {old_stage} to {kwargs['stage']}"
            )
            await self.activity_repo.create(activity)
        return deal

    async def close_deal(self, organization_id: UUID, deal_id: UUID, user_id: UUID) -> Optional[Deal]:
        member = await self.member_repo.get_by_org_and_user(organization_id, user_id)
        if not member:
            raise ValueError("access denied")
        if member.role == "member":
            raise ValueError("insufficient permissions")
        deal = await self.deal_repo.get_by_id(deal_id)
        if not deal or deal.organization_id != organization_id:
            return None
        if deal.status == "closed":
            raise ValueError("deal already closed")
        deal = await self.deal_repo.update(deal_id, status="closed", closed_at=datetime.utcnow())
        activity = Activity(
            organization_id=organization_id,
            user_id=user_id,
            deal_id=deal.id,
            type="deal_closed",
            description=f"deal '{deal.title}' closed"
        )
        await self.activity_repo.create(activity)
        return deal

    async def delete_deal(self, organization_id: UUID, deal_id: UUID, user_id: UUID) -> bool:
        member = await self.member_repo.get_by_org_and_user(organization_id, user_id)
        if not member:
            raise ValueError("access denied")
        if member.role not in ["owner", "admin"]:
            raise ValueError("insufficient permissions")
        deal = await self.deal_repo.get_by_id(deal_id)
        if not deal or deal.organization_id != organization_id:
            return False
        return await self.deal_repo.delete(deal_id)

