from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.organization import Organization
from src.repositories.base_repository import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    def __init__(self, session: AsyncSession):
        super().__init__(Organization, session)

    async def get_by_name(self, name: str) -> Optional[Organization]:
        result = await self.session.execute(
            select(Organization).where(Organization.name == name)
        )
        return result.scalar_one_or_none()

