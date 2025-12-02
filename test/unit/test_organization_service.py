import pytest
from uuid import uuid4

from src.services.organization_service import OrganizationService
from src.services.auth_service import AuthService
from src.models.user import User


@pytest.mark.asyncio
async def test_create_organization(db_session):
    auth_service = AuthService(db_session)
    user = await auth_service.register_user(
        email="owner@example.com",
        password="password123",
        full_name="owner"
    )
    org_service = OrganizationService(db_session)
    org = await org_service.create_organization("test org", user.id)
    assert org.name == "test org"
    members = await org_service.get_members(org.id)
    assert len(members) == 1
    assert members[0].user_id == user.id
    assert members[0].role == "owner"


@pytest.mark.asyncio
async def test_add_member(db_session):
    auth_service = AuthService(db_session)
    owner = await auth_service.register_user(
        email="owner@example.com",
        password="password123",
        full_name="owner"
    )
    member_user = await auth_service.register_user(
        email="member@example.com",
        password="password123",
        full_name="member"
    )
    org_service = OrganizationService(db_session)
    org = await org_service.create_organization("test org", owner.id)
    new_member = await org_service.add_member(org.id, member_user.id, "manager", owner.id)
    assert new_member.user_id == member_user.id
    assert new_member.role == "manager"


@pytest.mark.asyncio
async def test_add_member_insufficient_permissions(db_session):
    auth_service = AuthService(db_session)
    owner = await auth_service.register_user(
        email="owner@example.com",
        password="password123",
        full_name="owner"
    )
    member_user = await auth_service.register_user(
        email="member@example.com",
        password="password123",
        full_name="member"
    )
    org_service = OrganizationService(db_session)
    org = await org_service.create_organization("test org", owner.id)
    member = await org_service.add_member(org.id, member_user.id, "member", owner.id)
    with pytest.raises(ValueError):
        await org_service.add_member(org.id, uuid4(), "manager", member.user_id)

