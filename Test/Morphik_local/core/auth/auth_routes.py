from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
import hashlib
import secrets
import jwt
import asyncpg
import os

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Get JWT secret from environment
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Database connection
DATABASE_URL = os.getenv("POSTGRES_URI", "postgresql://morphik:morphik@postgres:5432/morphik")

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    username: str

class AuthResponse(BaseModel):
    token: str
    user: dict

def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hash password with SHA256 and salt"""
    if salt is None:
        salt = secrets.token_hex(32)
    
    # Combine password and salt, then hash
    password_salt = f"{password}{salt}".encode()
    password_hash = hashlib.sha256(password_salt).hexdigest()
    
    return password_hash, salt

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verify password against stored hash"""
    password_hash, _ = hash_password(password, salt)
    return password_hash == stored_hash

def create_jwt_token(user_id: int, email: str) -> str:
    """Create JWT token for user"""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register new user"""
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Check if user exists
        existing = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1 OR username = $2",
            request.email, request.username
        )
        
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Hash password with salt
        password_hash, salt = hash_password(request.password)
        
        # Create user
        user = await conn.fetchrow("""
            INSERT INTO users (email, username, password_hash, salt, created_at, updated_at)
            VALUES ($1, $2, $3, $4, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id, email, username, created_at
        """, request.email, request.username, password_hash, salt)
        
        # Create token
        token = create_jwt_token(user["id"], user["email"])
        
        return AuthResponse(
            token=token,
            user={
                "id": user["id"],
                "email": user["email"],
                "username": user["username"],
                "created_at": user["created_at"].isoformat()
            }
        )
    finally:
        await conn.close()

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login user"""
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Get user
        user = await conn.fetchrow("""
            SELECT id, email, username, password_hash, salt, created_at
            FROM users WHERE email = $1
        """, request.email)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        if not verify_password(request.password, user["password_hash"], user["salt"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create token
        token = create_jwt_token(user["id"], user["email"])
        
        return AuthResponse(
            token=token,
            user={
                "id": user["id"],
                "email": user["email"],
                "username": user["username"],
                "created_at": user["created_at"].isoformat()
            }
        )
    finally:
        await conn.close()

@router.get("/me")
async def get_current_user(authorization: str = None):
    """Get current user from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        conn = await asyncpg.connect(DATABASE_URL)
        try:
            user = await conn.fetchrow("""
                SELECT id, email, username, created_at
                FROM users WHERE id = $1
            """, payload["user_id"])
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return {
                "id": user["id"],
                "email": user["email"],
                "username": user["username"],
                "created_at": user["created_at"].isoformat()
            }
        finally:
            await conn.close()
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")