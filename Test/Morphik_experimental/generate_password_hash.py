import bcrypt

passwords = {
    "fedor": "usertest1",
    "testuser": "testpassword123"
}

for username, password in passwords.items():
    # Generate hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    print(f"{username}: {password}")
    print(f"Hash: {hashed.decode('utf-8')}")
    print()