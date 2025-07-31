from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
import hashlib
import secrets


class UserCreate(BaseModel):
    """User registration model."""
    username: str
    password: str
    email: Optional[str] = None


class UserLogin(BaseModel):
    """User login model."""
    username: str
    password: str


class UserResponse(BaseModel):
    """User response model without password."""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )
    
    id: str
    username: str
    email: Optional[str] = None
    created_at: datetime
    

class UserInDB(BaseModel):
    """User model as stored in database."""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )
    
    id: str
    username: str
    password_hash: str
    email: Optional[str] = None
    created_at: datetime
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA256 with salt."""
        salt = secrets.token_hex(32)
        pwd_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        return f"{salt}${pwd_hash}"
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash."""
        try:
            salt, pwd_hash = self.password_hash.split('$')
            return hashlib.sha256((password + salt).encode('utf-8')).hexdigest() == pwd_hash
        except ValueError:
            return False


class LoginResponse(BaseModel):
    """Response after successful login."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse