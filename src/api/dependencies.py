from typing import Optional
from uuid import UUID
from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.services.auth_service import AuthService
from src.services.organization_service import OrganizationService
from src.models.user import User
from src.models.organization_member import OrganizationMember


async def get_current_user(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="invalid token format")
    token = authorization.split(" ")[1]
    auth_service = AuthService(db)
    payload = auth_service.decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="invalid token")
    from src.repositories.user_repository import UserRepository
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(UUID(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="user not found")
    return user


async def get_organization_id(
    x_organization_id: Optional[str] = Header(None, alias="X-Organization-Id")
) -> UUID:
    if not x_organization_id:
        raise HTTPException(status_code=400, detail="X-Organization-Id header required")
    try:
        return UUID(x_organization_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid organization id")


async def get_organization_member(
    organization_id: UUID = Depends(get_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> OrganizationMember:
    org_service = OrganizationService(db)
    member = await org_service.check_access(organization_id, current_user.id)
    if not member:
        raise HTTPException(status_code=403, detail="access denied")
    return member

