from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.activity import Activity
from src.repositories.base_repository import BaseRepository


class ActivityRepository(BaseRepository[Activity]):
    def __init__(self, session: AsyncSession):
        super().__init__(Activity, session)

    async def get_by_organization(self, organization_id: UUID, skip: int = 0, limit: int = 100) -> List[Activity]:
        result = await self.session.execute(
            select(Activity)
            .options(selectinload(Activity.user))
            .where(Activity.organization_id == organization_id)
            .order_by(Activity.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_deal(self, organization_id: UUID, deal_id: UUID) -> List[Activity]:
        result = await self.session.execute(
            select(Activity)
            .options(selectinload(Activity.user))
            .where(
                Activity.organization_id == organization_id,
                Activity.deal_id == deal_id
            )
            .order_by(Activity.created_at.desc())
        )
        return list(result.scalars().all())

