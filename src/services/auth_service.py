from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import app_settings
from src.repositories.user_repository import UserRepository
from src.repositories.organization_member_repository import OrganizationMemberRepository
from src.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.member_repo = OrganizationMemberRepository(session)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=app_settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, app_settings.secret_key, algorithm=app_settings.algorithm)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=app_settings.refresh_token_expire_days)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, app_settings.secret_key, algorithm=app_settings.algorithm)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, app_settings.secret_key, algorithms=[app_settings.algorithm])
            return payload
        except JWTError:
            return None

    async def register_user(self, email: str, password: str, full_name: str) -> User:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ValueError("user already exists")
        hashed = self.get_password_hash(password)
        user = User(email=email, password_hash=hashed, full_name=full_name)
        return await self.user_repo.create(user)

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user

    async def get_user_organizations(self, user_id: UUID) -> list:
        memberships = await self.member_repo.get_by_user(user_id)
        return [m.organization for m in memberships]

