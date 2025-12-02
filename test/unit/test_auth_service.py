import pytest
from uuid import uuid4

from src.services.auth_service import AuthService
from src.models.user import User


@pytest.mark.asyncio
async def test_register_user(db_session):
    auth_service = AuthService(db_session)
    user = await auth_service.register_user(
        email="test@example.com",
        password="password123",
        full_name="test user"
    )
    assert user.email == "test@example.com"
    assert user.full_name == "test user"
    assert user.password_hash != "password123"


@pytest.mark.asyncio
async def test_register_duplicate_user(db_session):
    auth_service = AuthService(db_session)
    await auth_service.register_user(
        email="test@example.com",
        password="password123",
        full_name="test user"
    )
    with pytest.raises(ValueError):
        await auth_service.register_user(
            email="test@example.com",
            password="password123",
            full_name="test user"
        )


@pytest.mark.asyncio
async def test_authenticate_user(db_session):
    auth_service = AuthService(db_session)
    user = await auth_service.register_user(
        email="test@example.com",
        password="password123",
        full_name="test user"
    )
    authenticated = await auth_service.authenticate_user("test@example.com", "password123")
    assert authenticated is not None
    assert authenticated.id == user.id


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(db_session):
    auth_service = AuthService(db_session)
    await auth_service.register_user(
        email="test@example.com",
        password="password123",
        full_name="test user"
    )
    authenticated = await auth_service.authenticate_user("test@example.com", "wrongpassword")
    assert authenticated is None


@pytest.mark.asyncio
async def test_create_access_token():
    auth_service = AuthService(None)
    token = auth_service.create_access_token(data={"sub": str(uuid4())})
    assert token is not None
    assert isinstance(token, str)


@pytest.mark.asyncio
async def test_decode_token():
    auth_service = AuthService(None)
    user_id = str(uuid4())
    token = auth_service.create_access_token(data={"sub": user_id})
    payload = auth_service.decode_token(token)
    assert payload is not None
    assert payload["sub"] == user_id

