from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.services.task_service import TaskService
from src.api.dependencies import get_current_user, get_organization_member
from src.api.v1.schemas import TaskCreate, TaskUpdate, TaskResponse
from src.models.user import User
from src.models.organization_member import OrganizationMember

router = APIRouter()


@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    task_service = TaskService(db)
    try:
        task = await task_service.create_task(
            member.organization_id,
            current_user.id,
            task_data.title,
            task_data.description,
            task_data.deal_id,
            task_data.contact_id,
            task_data.assigned_to_id,
            task_data.due_date
        )
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    task_service = TaskService(db)
    tasks = await task_service.list_tasks(
        member.organization_id,
        current_user.id,
        skip,
        limit
    )
    return tasks


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    task_service = TaskService(db)
    task = await task_service.get_task(
        member.organization_id,
        task_id,
        current_user.id
    )
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    task_service = TaskService(db)
    update_data = task_data.model_dump(exclude_unset=True)
    try:
        task = await task_service.update_task(
            member.organization_id,
            task_id,
            current_user.id,
            **update_data
        )
        if not task:
            raise HTTPException(status_code=404, detail="task not found")
        return task
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    task_service = TaskService(db)
    try:
        task = await task_service.complete_task(
            member.organization_id,
            task_id,
            current_user.id
        )
        if not task:
            raise HTTPException(status_code=404, detail="task not found")
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    member: OrganizationMember = Depends(get_organization_member),
    db: AsyncSession = Depends(get_db)
):
    task_service = TaskService(db)
    try:
        result = await task_service.delete_task(
            member.organization_id,
            task_id,
            current_user.id
        )
        if not result:
            raise HTTPException(status_code=404, detail="task not found")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

