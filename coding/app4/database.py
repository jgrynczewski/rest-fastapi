"""Database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session
from typing import Generator
from config import settings


engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides database session."""
    with Session(engine) as session:
        yield session