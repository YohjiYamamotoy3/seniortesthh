from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.organization_repository import OrganizationRepository
from src.repositories.organization_member_repository import OrganizationMemberRepository
from src.models.organization import Organization
from src.models.organization_member import OrganizationMember


class OrganizationService:
    def __init__(self, session: AsyncSession):
        self.org_repo = OrganizationRepository(session)
        self.member_repo = OrganizationMemberRepository(session)

    async def create_organization(self, name: str, owner_id: UUID) -> Organization:
        org = Organization(name=name)
        org = await self.org_repo.create(org)
        member = OrganizationMember(
            organization_id=org.id,
            user_id=owner_id,
            role="owner"
        )
        await self.member_repo.create(member)
        return org

    async def add_member(self, organization_id: UUID, user_id: UUID, role: str, current_user_id: UUID) -> OrganizationMember:
        current_member = await self.member_repo.get_by_org_and_user(organization_id, current_user_id)
        if not current_member:
            raise ValueError("access denied")
        if current_member.role not in ["owner", "admin"]:
            raise ValueError("insufficient permissions")
        if role not in ["owner", "admin", "manager", "member"]:
            raise ValueError("invalid role")
        existing = await self.member_repo.get_by_org_and_user(organization_id, user_id)
        if existing:
            raise ValueError("user already member")
        member = OrganizationMember(
            organization_id=organization_id,
            user_id=user_id,
            role=role
        )
        return await self.member_repo.create(member)

    async def get_organization(self, organization_id: UUID) -> Optional[Organization]:
        return await self.org_repo.get_by_id(organization_id)

    async def get_members(self, organization_id: UUID) -> List[OrganizationMember]:
        return await self.member_repo.get_by_organization(organization_id)

    async def check_access(self, organization_id: UUID, user_id: UUID) -> Optional[OrganizationMember]:
        return await self.member_repo.get_by_org_and_user(organization_id, user_id)

