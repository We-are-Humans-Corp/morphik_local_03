#!/usr/bin/env python3
"""Script to create or update users in Morphik database."""

import psycopg2
import hashlib
import secrets
import sys
from datetime import datetime

# Database connection parameters
DB_CONFIG = {
    'host': '135.181.106.12',
    'port': 5432,
    'database': 'morphik',
    'user': 'morphik',
    'password': 'morphik'
}

def hash_password(password: str) -> str:
    """Hash password using SHA256 with salt (same as backend)."""
    salt = secrets.token_hex(32)
    pwd_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return f"{salt}${pwd_hash}"

def create_or_update_user(email: str, password: str):
    """Create a new user or update existing user's password."""
    conn = None
    cursor = None
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE email = %s OR username = %s", (email, email))
        existing_user = cursor.fetchone()
        
        password_hash = hash_password(password)
        
        if existing_user:
            # Update existing user's password
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE email = %s OR username = %s",
                (password_hash, email, email)
            )
            print(f"✅ Updated password for user: {email}")
        else:
            # Create new user
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, created_at) VALUES (%s, %s, %s, %s)",
                (email, email, password_hash, datetime.now())
            )
            print(f"✅ Created new user: {email}")
        
        conn.commit()
        print(f"Password: {password}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def main():
    print("=== Morphik User Manager ===\n")
    
    # Create test user
    print("Creating/updating test user...")
    create_or_update_user("test@example.com", "testpassword123")
    
    # Also update fedor@example.com
    print("\nUpdating fedor@example.com...")
    create_or_update_user("fedor@example.com", "testpassword123")
    
    print("\n✅ Done! You can now login with:")
    print("  - test@example.com / testpassword123")
    print("  - fedor@example.com / testpassword123")

if __name__ == "__main__":
    main()