from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class OrganizationCreate(BaseModel):
    name: str


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class MemberAdd(BaseModel):
    user_id: UUID
    role: str


class MemberResponse(BaseModel):
    id: UUID
    organization_id: UUID
    user_id: UUID
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class ContactCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None


class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None


class ContactResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    email: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DealCreate(BaseModel):
    contact_id: UUID
    title: str
    value: Optional[float] = None
    stage: str = "new"
    notes: Optional[str] = None


class DealUpdate(BaseModel):
    title: Optional[str] = None
    value: Optional[float] = None
    stage: Optional[str] = None
    notes: Optional[str] = None


class DealResponse(BaseModel):
    id: UUID
    organization_id: UUID
    contact_id: UUID
    title: str
    value: Optional[float]
    stage: str
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime]

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    deal_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None
    assigned_to_id: Optional[UUID] = None
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deal_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None
    assigned_to_id: Optional[UUID] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskResponse(BaseModel):
    id: UUID
    organization_id: UUID
    deal_id: Optional[UUID]
    contact_id: Optional[UUID]
    assigned_to_id: Optional[UUID]
    title: str
    description: Optional[str]
    status: str
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ActivityResponse(BaseModel):
    id: UUID
    organization_id: UUID
    user_id: UUID
    deal_id: Optional[UUID]
    contact_id: Optional[UUID]
    task_id: Optional[UUID]
    type: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DealsSummaryResponse(BaseModel):
    total: int
    total_value: float
    avg_value: float


class DealsFunnelResponse(BaseModel):
    new: int
    qualification: int
    proposal: int
    negotiation: int
    closed: int

