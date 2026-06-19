"""Authentication endpoints: register, login, me."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from dependencies import DbSession, CurrentUser
from models import User
from schemas import UserCreate, UserLogin, UserResponse, Token
# FastAPI NIE ma domyślnego hashowania haseł!
# Używamy passlib[bcrypt] - najpopularniejsza biblioteka do hashowania (cost=12, ~0.3s/hash)
# Alternatywy: argon2, scrypt (ale bcrypt jest standardem w FastAPI community)
from security import hash_password, verify_password, create_access_token


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def register(user: UserCreate, db: DbSession):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.execute(
        select(User).where(User.email == user.email)
    ).scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password and create user
    password_hash = hash_password(user.password)
    db_user = User(
        email=user.email,
        password_hash=password_hash,
        role=user.role  # Domyślnie USER (z UserCreate schema)
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: DbSession):
    """Login and get JWT token."""
    # Find user by email
    user = db.execute(
        select(User).where(User.email == credentials.email)
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create JWT token
    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: CurrentUser):
    """Get current user data (requires authentication)."""
    return current_user
