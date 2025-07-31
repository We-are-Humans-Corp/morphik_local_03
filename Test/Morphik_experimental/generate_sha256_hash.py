import hashlib
import secrets

def hash_password(password: str) -> str:
    """Hash password using SHA256 with salt."""
    salt = secrets.token_hex(32)
    pwd_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return f"{salt}${pwd_hash}"

passwords = {
    "fedor": "usertest1",
    "testuser": "testpassword123"
}

for username, password in passwords.items():
    hashed = hash_password(password)
    print(f"-- Update {username}")
    print(f"UPDATE users SET password_hash = '{hashed}' WHERE username = '{username}';")
    print()