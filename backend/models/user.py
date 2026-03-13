from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from passlib.context import CryptContext
from models.base import Base

# Password hashing context with proper handling for bcrypt 72-byte limit
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b",
    bcrypt__min_rounds=12
)


class UserDB(Base):
    """
    User model representing a registered user.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserCreate(BaseModel):
    """
    Schema for creating a new user.
    """
    email: str
    password: str
    name: Optional[str] = None


class UserRead(BaseModel):
    """
    Schema for returning user data.
    """
    id: int
    email: str
    name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserLogin(BaseModel):
    """
    Schema for user login.
    """
    email: str
    password: str


def hash_password(password: str) -> str:
    """
    Hash a plain text password.
    Note: bcrypt has a 72-byte password length limit, so we use the utility function.
    """
    from utils.password_utils import hash_bcrypt_password
    return hash_bcrypt_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against its hash.
    Note: bcrypt has a 72-byte password length limit, so we use the utility function.
    """
    from utils.password_utils import verify_bcrypt_password
    return verify_bcrypt_password(plain_password, hashed_password)