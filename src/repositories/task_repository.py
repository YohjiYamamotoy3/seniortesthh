from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.task import Task
from src.repositories.base_repository import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession):
        super().__init__(Task, session)

    async def get_by_organization(self, organization_id: UUID, skip: int = 0, limit: int = 100) -> List[Task]:
        result = await self.session.execute(
            select(Task)
            .options(selectinload(Task.assigned_to))
            .where(Task.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_user(self, organization_id: UUID, user_id: UUID) -> List[Task]:
        result = await self.session.execute(
            select(Task).where(
                Task.organization_id == organization_id,
                Task.assigned_to_id == user_id
            )
        )
        return list(result.scalars().all())

