from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.task_repository import TaskRepository
from src.repositories.deal_repository import DealRepository
from src.repositories.contact_repository import ContactRepository
from src.repositories.organization_member_repository import OrganizationMemberRepository
from src.repositories.activity_repository import ActivityRepository
from src.models.task import Task
from src.models.activity import Activity


class TaskService:
    def __init__(self, session: AsyncSession):
        self.task_repo = TaskRepository(session)
        self.deal_repo = DealRepository(session)
        self.contact_repo = ContactRepository(session)
        self.member_repo = OrganizationMemberRepository(session)
        self.activity_repo = ActivityRepository(session)

    async def create_task(self, organization_id: UUID, user_id: UUID, title: str,
                         description: Optional[str] = None, deal_id: Optional[UUID] = None,
                         contact_id: Optional[UUID] = None, assigned_to_id: Optional[UUID] = None,
                         due_date: Optional[datetime] = None) -> Task:
        member = await self.member_repo.get_by_org_and_user(organization_id, user_id)
        if not member:
            raise ValueError("access denied")
        if deal_id:
            deal = await self.deal_repo.get_by_id(deal_id)
            if not deal or deal.organization_id != organization_id:
                raise ValueError("deal not found")
        if contact_id:
            contact = await self.contact_repo.get_by_id(contact_id)
            if not contact or contact.organization_id != organization_id:
                raise ValueError("contact not found")
        task = Task(
            organization_id=organization_id,
            title=title,
            description=description,
            deal_id=deal_id,
            contact_id=contact_id,
            assigned_to_id=assigned_to_id,
            due_date=due_date
        )
        task = await self.task_repo.create(task)
        activity = Activity(
            organization_id=organization_id,
            user_id=user_id,
            task_id=task.id,
            type="task_created",
            description=f"task '{title}' created"
        )
        await self.activity_repo.create(activity)
        return task

    async def get_task(self, organization_id: UUID, task_id: UUID, user_id: UUID) -> Optional[Task]:
        member = await self.member_repo.get_by_org_and_user(organization_id, user_id)
        if not member:
            raise ValueError("access denied")
        task = await self.task_repo.get_by_id(task_id)
        if task and task.organization_id != organization_id:
            return None
        return task

    async def list_tasks(self, organization_id: UUID, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Task]:
        member = await self.member_repo.get_by_org_and_user(organization_id, user_id)
        if not member:
            raise ValueError("access denied")
        return await self.task_repo.get_by_organization(organization_id, skip, limit)

    async def update_task(self, organization_id: UUID, task_id: UUID, user_id: UUID, **kwargs) -> Optional[Task]:
        member = await self.member_repo.get_by_org_and_user(organization_id, user_id)
        if not member:
            raise ValueError("access denied")
        task = await self.task_repo.get_by_id(task_id)
        if not task or task.organization_id != organization_id:
            return None
        if member.role == "member" and task.assigned_to_id != user_id:
            raise ValueError("insufficient permissions")
        return await self.task_repo.update(task_id, **kwargs)

    async def complete_task(self, organization_id: UUID, task_id: UUID, user_id: UUID) -> Optional[Task]:
        member = await self.member_repo.get_by_org_and_user(organization_id, user_id)
        if not member:
            raise ValueError("access denied")
        task = await self.task_repo.get_by_id(task_id)
        if not task or task.organization_id != organization_id:
            return None
        if task.status == "completed":
            raise ValueError("task already completed")
        task = await self.task_repo.update(task_id, status="completed", completed_at=datetime.utcnow())
        activity = Activity(
            organization_id=organization_id,
            user_id=user_id,
            task_id=task.id,
            type="task_completed",
            description=f"task '{task.title}' completed"
        )
        await self.activity_repo.create(activity)
        return task

    async def delete_task(self, organization_id: UUID, task_id: UUID, user_id: UUID) -> bool:
        member = await self.member_repo.get_by_org_and_user(organization_id, user_id)
        if not member:
            raise ValueError("access denied")
        if member.role == "member":
            raise ValueError("insufficient permissions")
        task = await self.task_repo.get_by_id(task_id)
        if not task or task.organization_id != organization_id:
            return False
        return await self.task_repo.delete(task_id)

