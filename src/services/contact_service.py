from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.contact_repository import ContactRepository
from src.repositories.organization_member_repository import OrganizationMemberRepository
from src.models.contact import Contact


class ContactService:
    def __init__(self, session: AsyncSession):
        self.contact_repo = ContactRepository(session)
        self.member_repo = OrganizationMemberRepository(session)

    async def create_contact(self, organization_id: UUID, user_id: UUID, name: str, email: Optional[str] = None,
                             phone: Optional[str] = None, company: Optional[str] = None,
                             notes: Optional[str] = None) -> Contact:
        member = await self.member_repo.get_by_org_and_user(organization_id, user_id)
        if not member:
            raise ValueError("access denied")
        contact = Contact(
            organization_id=organization_id,
            name=name,
            email=email,
            phone=phone,
            company=company,
            notes=notes
        )
        return await self.contact_repo.create(contact)

    async def get_contact(self, organization_id: UUID, contact_id: UUID, user_id: UUID) -> Optional[Contact]:
        member = await self.member_repo.get_by_org_and_user(organization_id, user_id)
        if not member:
            raise ValueError("access denied")
        contact = await self.contact_repo.get_by_id(contact_id)
        if contact and contact.organization_id != organization_id:
            return None
        return contact

    async def list_contacts(self, organization_id: UUID, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Contact]:
        member = await self.member_repo.get_by_org_and_user(organization_id, user_id)
        if not member:
            raise ValueError("access denied")
        return await self.contact_repo.get_by_organization(organization_id, skip, limit)

    async def update_contact(self, organization_id: UUID, contact_id: UUID, user_id: UUID, **kwargs) -> Optional[Contact]:
        member = await self.member_repo.get_by_org_and_user(organization_id, user_id)
        if not member:
            raise ValueError("access denied")
        if member.role == "member":
            raise ValueError("insufficient permissions")
        contact = await self.contact_repo.get_by_id(contact_id)
        if not contact or contact.organization_id != organization_id:
            return None
        return await self.contact_repo.update(contact_id, **kwargs)

    async def delete_contact(self, organization_id: UUID, contact_id: UUID, user_id: UUID) -> bool:
        member = await self.member_repo.get_by_org_and_user(organization_id, user_id)
        if not member:
            raise ValueError("access denied")
        if member.role not in ["owner", "admin"]:
            raise ValueError("insufficient permissions")
        contact = await self.contact_repo.get_by_id(contact_id)
        if not contact or contact.organization_id != organization_id:
            return False
        return await self.contact_repo.delete(contact_id)

