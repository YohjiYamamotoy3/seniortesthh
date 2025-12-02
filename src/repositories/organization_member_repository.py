from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.organization_member import OrganizationMember
from src.repositories.base_repository import BaseRepository


class OrganizationMemberRepository(BaseRepository[OrganizationMember]):
    def __init__(self, session: AsyncSession):
        super().__init__(OrganizationMember, session)

    async def get_by_org_and_user(self, organization_id: UUID, user_id: UUID) -> Optional[OrganizationMember]:
        result = await self.session.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_organization(self, organization_id: UUID) -> List[OrganizationMember]:
        result = await self.session.execute(
            select(OrganizationMember)
            .options(selectinload(OrganizationMember.user))
            .where(OrganizationMember.organization_id == organization_id)
        )
        return list(result.scalars().all())

    async def get_by_user(self, user_id: UUID) -> List[OrganizationMember]:
        result = await self.session.execute(
            select(OrganizationMember)
            .options(selectinload(OrganizationMember.organization))
            .where(OrganizationMember.user_id == user_id)
        )
        return list(result.scalars().all())

