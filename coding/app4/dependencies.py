"""Reusable FastAPI dependencies with Annotated types."""

from typing import Annotated
from fastapi import Depends, Path
from sqlalchemy.orm import Session
from database import get_db
from security import get_current_user, require_admin
from models import User


# Database session dependency (to nam zastępuje zapis db: Session = Depends(get_db))
DbSession = Annotated[Session, Depends(get_db)]

# Path parameter for positive integers (IDs) (to nam zastępuje zapis task_id = Path(ge=1))
PositiveInt = Annotated[int, Path(ge=1)]

# Current user dependency (to nam zastępuje zapis current_user: User = Depends(get_current_user))
CurrentUser = Annotated[User, Depends(get_current_user)]

# Admin user dependency (to nam zastępuje zapis admin_user: User = Depends(require_admin))
AdminUser = Annotated[User, Depends(require_admin)]