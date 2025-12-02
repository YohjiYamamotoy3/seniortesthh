from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.contact import Contact
from src.repositories.base_repository import BaseRepository


class ContactRepository(BaseRepository[Contact]):
    def __init__(self, session: AsyncSession):
        super().__init__(Contact, session)

    async def get_by_organization(self, organization_id: UUID, skip: int = 0, limit: int = 100) -> List[Contact]:
        result = await self.session.execute(
            select(Contact)
            .where(Contact.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

