т# Morphik Self-Hosted - Git Repository Setup

## 🔐 Authentication Credentials

### Default User Account
```
Username: testuser
Password: testpass123
```

### API Access
```
API URL: http://localhost:8000
UI URL: http://localhost:3000
```

## 📁 Modified Files List

### New Files Created
```
✅ /core/models/user.py                    # User authentication model
✅ /core/routes/auth.py                    # Authentication endpoints
✅ /migrations/add_users_table.sql         # Database migration for users
✅ /docs/MORPHIK_SETUP_COMPLETE.md         # Full setup documentation
✅ /docs/MORPHIK_DEPLOYMENT_GUIDE.md       # Deployment guide
✅ /docs/MORPHIK_CHANGELOG.md              # Change history
```

### Modified Files
```
📝 /core/api.py                            # Added model name mapping (lines 631-640)
📝 /core/routes/models.py                  # Added /custom endpoint
📝 /ee/ui-component/components/chat/ModelSelector.tsx  # Removed API key filtering
📝 /.env                                   # Added API keys and configuration
📝 /morphik.toml                           # Fixed model configurations
📝 /.env.example                           # Updated with all variables
```

## 🚀 Quick Setup Instructions

### 1. Clone Repository
```bash
git clone <your-repository-url>
cd morphik-core
```

### 2. Environment Setup
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys:
ANTHROPIC_API_KEY=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
JWT_SECRET_KEY=your-secret-key-here
SESSION_SECRET_KEY=your-session-secret-here
```

### 3. Start Services
```bash
# Use official docker-compose
docker-compose -f docker-compose-official.yml up -d

# Wait for services to start
sleep 30

# Run database migrations
docker exec morphik-core-morphik-1 python -m alembic upgrade head
docker exec morphik-core-morphik-1 psql -U morphik -d morphik -f /app/migrations/add_users_table.sql
```

### 4. Access Application
1. Open UI: http://localhost:3000
2. Click "Login" 
3. Use credentials:
   - Username: `testuser`
   - Password: `testpass123`
4. Select any Claude model from dropdown
5. Start chatting!

## 📋 Complete Change Summary

### Authentication System
- Added complete user authentication from scratch
- JWT-based token system
- Secure password hashing (SHA256 + salt)
- Login/Register endpoints

### Model Integration Fix
- Fixed "LLM Provider NOT provided" error
- Added automatic model name mapping
- UI sends: `claude_opus`
- Backend converts to: `anthropic/claude-3-opus-20240229`

### UI Modifications
- Removed API key filtering in model selector
- Shows all models in self-hosted mode
- Backend validates API keys

### Database Changes
```sql
-- New users table
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Configuration Files

### morphik.toml
```toml
[mode]
mode = "self_hosted"

[registered_models]
claude_opus = { model_name = "anthropic/claude-3-opus-20240229" }
claude_sonnet = { model_name = "anthropic/claude-3-5-sonnet-latest" }
claude_haiku = { model_name = "anthropic/claude-3-haiku-20240307" }
```

### .env
```env
DATABASE_URL=postgresql://morphik:morphik@postgres:5432/morphik
ANTHROPIC_API_KEY=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
JWT_SECRET_KEY=your-secret-key-here
SESSION_SECRET_KEY=your-session-secret-here
MODE=self_hosted
```

## 🐛 Troubleshooting

### Problem: Can't login
```bash
# Check if auth endpoints are loaded
curl http://localhost:8000/auth/login

# Check logs
docker logs morphik-core-morphik-1 | grep auth
```

### Problem: Models not showing
```bash
# Check registered models
curl http://localhost:8000/models/custom

# Verify environment
docker exec morphik-core-morphik-1 env | grep ANTHROPIC
```

### Problem: Chat not working
```bash
# Check logs for errors
docker logs morphik-core-morphik-1 --tail 100 | grep -E "(litellm|model|error)"

# Test API directly
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{"query": "Hello", "llm_config": {"model": "claude_opus"}}'
```

## 📦 Git Commands

### Initial Commit
```bash
# Add all changes
git add .

# Commit with descriptive message
git commit -m "feat: Add authentication system and fix Claude model integration

- Implement complete user authentication (register/login)
- Add JWT-based authorization
- Fix model name mapping for LiteLLM compatibility
- Update UI to show all models in self-hosted mode
- Add database migration for users table
- Configure Claude models in morphik.toml"

# Push to repository
git push origin main
```

### Create Release Tag
```bash
git tag -a v1.0.0 -m "First stable release with authentication and Claude support"
git push origin v1.0.0
```

## 🔗 Important Links

- **Main Documentation**: `/docs/MORPHIK_SETUP_COMPLETE.md`
- **Deployment Guide**: `/docs/MORPHIK_DEPLOYMENT_GUIDE.md`
- **Change Log**: `/docs/MORPHIK_CHANGELOG.md`

## ⚠️ Security Notes

1. **Change default credentials** before production deployment
2. **Generate new JWT secrets** for production
3. **Use environment-specific API keys**
4. **Enable HTTPS** in production
5. **Configure firewall rules** appropriately

## 📝 Notes

- All modifications preserve original Morphik functionality
- Authentication system is custom-built for self-hosted mode
- Model configuration follows LiteLLM standards
- Database migrations are idempotent (safe to run multiple times)