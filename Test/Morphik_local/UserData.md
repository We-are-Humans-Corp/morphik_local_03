# User Authentication Data

## Current Active Users

The system has the following users configured and ready for use:

### Test Account
- **Username/Email**: `test@example.com`
- **Password**: `testpassword123`
- **Created**: 2025-08-18
- **Purpose**: General testing and demonstration

### Admin Account
- **Username/Email**: `fedor@example.com`
- **Password**: `testpassword123`
- **Created**: 2025-08-09 (updated 2025-08-18)
- **Purpose**: Administrative access

## Authentication Details

### Login URL
- **UI Login**: http://localhost:3000/login
- **API Endpoint**: http://localhost:8000/auth/login

### API Authentication
To authenticate via API, send a POST request:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test@example.com", "password": "testpassword123"}'
```

### Password Hashing
The system uses SHA256 with salt for password hashing. Format: `{salt}${hash}`

## User Management Script

A utility script `create_user.py` is available for user management:

### Location
`/Test/Morphik_local/create_user.py`

### Usage
```bash
python create_user.py
```

This script will:
1. Create new users if they don't exist
2. Update passwords for existing users
3. Use the correct password hashing format (SHA256 with salt)

### Requirements
- Python 3.x
- psycopg2-binary
- Direct access to PostgreSQL database (135.181.106.12:5432)

## Database Information

### PostgreSQL Connection
- **Host**: 135.181.106.12
- **Port**: 5432
- **Database**: morphik
- **Username**: morphik
- **Password**: morphik

### Users Table Structure
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Troubleshooting

### If login fails:
1. Check that backend is running: `docker ps`
2. Verify API is accessible: `curl http://localhost:8000/ping`
3. Test login via API directly (see API Authentication above)
4. Re-run the user creation script if needed

### Common Issues:
- **"Incorrect username or password"**: Password might be using wrong hash format. Re-run `create_user.py`
- **Connection refused**: Check if all services are running with `docker compose ps`
- **UI shows no models**: Check Ollama service and API key configuration

## Security Notes

⚠️ **Important**: 
- The current passwords are for development/testing only
- In production, use strong, unique passwords
- Never commit real credentials to version control
- Consider implementing 2FA for production deployments