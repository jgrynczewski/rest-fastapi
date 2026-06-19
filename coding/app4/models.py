"""SQLAlchemy ORM models."""

import enum
from sqlalchemy import Integer, String, Enum
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class UserRole(enum.Enum):
    """User roles for authorization."""
    USER = "user"
    ADMIN = "admin"


class Task(Base):
    """Task model."""
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    def __repr__(self):
        return f"<Task(id={self.id}, name='{self.name}')>"


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role={self.role})>"
