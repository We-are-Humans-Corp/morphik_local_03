import logging
import uuid
from datetime import datetime, timedelta, UTC
from typing import Dict, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy import text

from core.config import get_settings
from core.models.user import UserCreate, UserLogin, UserResponse, UserInDB, LoginResponse
from core.services_init import document_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])

settings = get_settings()


async def get_user_by_username(username: str) -> Optional[UserInDB]:
    """Get user by username from database."""
    try:
        async with document_service.db.engine.begin() as conn:
            query = text("""
                SELECT id, username, password_hash, email, created_at 
                FROM users 
                WHERE username = :username
            """)
            
            result = await conn.execute(query, {"username": username})
            row = result.fetchone()
            
            if row:
                return UserInDB(
                    id=str(row[0]),
                    username=row[1],
                    password_hash=row[2],
                    email=row[3],
                    created_at=row[4]
                )
            return None
    except Exception as e:
        logger.error(f"Error getting user by username: {e}")
        return None


async def create_user(user: UserCreate) -> UserInDB:
    """Create new user in database."""
    try:
        user_id = str(uuid.uuid4())
        password_hash = UserInDB.hash_password(user.password)
        
        async with document_service.db.engine.begin() as conn:
            query = text("""
                INSERT INTO users (id, username, password_hash, email)
                VALUES (:id, :username, :password_hash, :email)
                RETURNING id, username, password_hash, email, created_at
            """)
            
            result = await conn.execute(
                query,
                {
                    "id": user_id,
                    "username": user.username,
                    "password_hash": password_hash,
                    "email": user.email
                }
            )
            
            row = result.fetchone()
            if row:
                return UserInDB(
                    id=str(row[0]),
                    username=row[1],
                    password_hash=row[2],
                    email=row[3],
                    created_at=row[4]
                )
            raise Exception("Failed to create user")
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise


def create_access_token(user_id: str, username: str) -> str:
    """Create JWT access token."""
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode = {
        "entity_id": user_id,
        "entity_type": "user",
        "user_id": user_id,
        "username": username,
        "permissions": ["read", "write"],
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


@router.post("/register", response_model=LoginResponse)
async def register(user_create: UserCreate):
    """Register new user."""
    # Check if user already exists
    existing_user = await get_user_by_username(user_create.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user
    try:
        user = await create_user(user_create)
        
        # Create access token
        access_token = create_access_token(user.id, user.username)
        
        return LoginResponse(
            access_token=access_token,
            user=UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                created_at=user.created_at
            )
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post("/login", response_model=LoginResponse)
async def login(user_login: UserLogin):
    """Login user."""
    # Get user from database
    user = await get_user_by_username(user_login.username)
    
    if not user or not user.verify_password(user_login.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(user.id, user.username)
    
    return LoginResponse(
        access_token=access_token,
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(authorization: str = Header(None)):
    """Get current user info."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    token = authorization[7:]  # Remove "Bearer " prefix
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("user_id")
        username = payload.get("username")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get fresh user data
        user = await get_user_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )