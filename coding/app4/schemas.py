"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, Field, ConfigDict, EmailStr
from models import UserRole


class TaskBase(BaseModel):
    """Base Task schema with shared fields."""
    name: str = Field(min_length=3, max_length=100, description="Nazwa zadania")


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    name: str = Field(min_length=1, max_length=100, description="Nazwa zadania")


class TaskResponse(TaskBase):
    """Schema for task response."""
    id: int

    model_config = ConfigDict(from_attributes=True)


# Authentication schemas
class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(min_length=8, description="Hasło min 8 znaków")
    role: UserRole = UserRole.USER  # Domyślnie USER (admin musi ustawić ręcznie w bazie)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    email: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str