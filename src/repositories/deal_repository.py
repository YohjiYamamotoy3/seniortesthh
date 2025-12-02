from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.models.deal import Deal
from src.repositories.base_repository import BaseRepository


class DealRepository(BaseRepository[Deal]):
    def __init__(self, session: AsyncSession):
        super().__init__(Deal, session)

    async def get_by_organization(self, organization_id: UUID, skip: int = 0, limit: int = 100) -> List[Deal]:
        result = await self.session.execute(
            select(Deal)
            .options(selectinload(Deal.contact))
            .where(Deal.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_stage(self, organization_id: UUID, stage: str) -> List[Deal]:
        result = await self.session.execute(
            select(Deal).where(
                Deal.organization_id == organization_id,
                Deal.stage == stage
            )
        )
        return list(result.scalars().all())

    async def get_summary(self, organization_id: UUID) -> dict:
        result = await self.session.execute(
            select(
                func.count(Deal.id).label("total"),
                func.sum(Deal.value).label("total_value"),
                func.avg(Deal.value).label("avg_value")
            ).where(
                Deal.organization_id == organization_id,
                Deal.status == "closed"
            )
        )
        row = result.first()
        return {
            "total": row.total or 0,
            "total_value": float(row.total_value or 0),
            "avg_value": float(row.avg_value or 0)
        }

    async def get_funnel(self, organization_id: UUID) -> dict:
        stages = ["new", "qualification", "proposal", "negotiation", "closed"]
        funnel = {}
        for stage in stages:
            result = await self.session.execute(
                select(func.count(Deal.id)).where(
                    Deal.organization_id == organization_id,
                    Deal.stage == stage
                )
            )
            count = result.scalar() or 0
            funnel[stage] = count
        return funnel

