import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, UTC
import hashlib
import secrets

# Test password hashing
def hash_password(password: str) -> str:
    """Hash password using SHA256 with salt."""
    salt = secrets.token_hex(32)
    pwd_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return f"{salt}${pwd_hash}"

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    try:
        salt, pwd_hash = password_hash.split('$')
        return hashlib.sha256((password + salt).encode('utf-8')).hexdigest() == pwd_hash
    except ValueError:
        return False

# Test basic functionality
print("Testing password hashing...")
password = "testpass123"
hashed = hash_password(password)
print(f"Password: {password}")
print(f"Hashed: {hashed}")
print(f"Verify correct password: {verify_password(password, hashed)}")
print(f"Verify wrong password: {verify_password('wrongpass', hashed)}")

# Test database connection
async def test_db():
    from sqlalchemy import create_async_engine, text
    from sqlalchemy.ext.asyncio import AsyncSession
    
    # Use the same connection string as in docker-compose
    DATABASE_URL = "postgresql+asyncpg://morphik:morphik@localhost:5432/morphik"
    
    try:
        engine = create_async_engine(DATABASE_URL)
        
        async with engine.begin() as conn:
            # Check if users table exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'users'
                )
            """))
            exists = result.scalar()
            print(f"\nUsers table exists: {exists}")
            
            if exists:
                # Try to insert a test user
                user_id = "test-" + secrets.token_hex(8)
                username = "testuser_" + secrets.token_hex(4)
                password_hash = hash_password("testpass123")
                created_at = datetime.now(UTC)
                
                print(f"\nInserting test user: {username}")
                
                result = await conn.execute(
                    text("""
                        INSERT INTO users (id, username, password_hash, email, created_at, updated_at)
                        VALUES (:id, :username, :password_hash, :email, :created_at, :updated_at)
                        RETURNING id, username, password_hash, email, created_at
                    """),
                    {
                        "id": user_id,
                        "username": username,
                        "password_hash": password_hash,
                        "email": "test@example.com",
                        "created_at": created_at,
                        "updated_at": created_at
                    }
                )
                
                row = result.fetchone()
                print(f"Inserted row: {row}")
                print(f"Row type: {type(row)}")
                if row:
                    print(f"ID: {row[0]}")
                    print(f"Username: {row[1]}")
                    print(f"Password hash: {row[2]}")
                    print(f"Email: {row[3]}")
                    print(f"Created at: {row[4]}")
                
                # Try to fetch the user back
                result = await conn.execute(
                    text("""
                        SELECT id, username, password_hash, email, created_at 
                        FROM users 
                        WHERE username = :username
                    """),
                    {"username": username}
                )
                
                row = result.fetchone()
                print(f"\nFetched user: {row}")
                
        await engine.dispose()
        
    except Exception as e:
        print(f"\nDatabase error: {e}")
        import traceback
        traceback.print_exc()

# Run the async test
print("\n" + "="*50)
print("Testing database connection...")
print("="*50)
asyncio.run(test_db())