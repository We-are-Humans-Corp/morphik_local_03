# Morphik Setup Complete Guide

## Current System Status

### ✅ Services Running
All Docker services are successfully deployed and operational:

- **morphik** (API Server) - Port 8000
- **postgres** (Database) - Port 5432
- **redis** (Cache/Queue) - Port 6379
- **worker** (Background Jobs) - Running
- **ollama** (Local LLM) - Port 11434
- **ui** (Frontend) - Port 3000

### ✅ Configuration Completed

#### Environment Variables Set
```bash
JWT_SECRET_KEY=your-secret-key-8b3d4f2ea1e4c9a5b7d6f3e2c1a8b5d4f7e9c2b6a4d8f1e3c7b9a5d2f6e8c4
JWT_ALGORITHM=HS256
POSTGRES_USER=morphik
POSTGRES_PASSWORD=morphik123
POSTGRES_DB=morphik_db
REDIS_HOST=redis
REDIS_PORT=6379
ANTHROPIC_API_KEY=sk-ant-api03-... # Added but using Ollama locally
```

#### Models Configured
```toml
# morphik.toml
[registered_models]
# Ollama models (local)
ollama_llama = { model_name = "ollama/llama3.2:3b", api_base = "http://ollama:11434" }
ollama_embed = { model_name = "ollama/nomic-embed-text", api_base = "http://ollama:11434" }

# Cloud models (available with API keys)
claude_sonnet = { model_name = "anthropic/claude-3-5-sonnet-latest" }
gpt_4 = { model_name = "openai/gpt-4-turbo-preview" }
gemini_pro = { model_name = "google/gemini-pro" }
```

### ✅ Authentication System

#### Implementation Details
- **Password Hashing**: SHA256 with salt
- **Token Type**: JWT with 7-day expiration
- **Session Management**: Redis-backed
- **Test Account Created**:
  - Username: `testuser`
  - Password: `testpassword123`
  - Email: `test@example.com`

#### Fixed Issues
1. DateTime timezone consistency (using UTC)
2. Database query parameter alignment
3. ESLint build errors in UI
4. Model configuration mapping

### ✅ Database Schema

Tables created and populated:
- `users` - User authentication
- `documents` - Document storage
- `chunks` - Document chunks with embeddings
- `chat_sessions` - Chat history
- `knowledge_graph_entities` - Knowledge graph nodes
- `knowledge_graph_relationships` - Knowledge graph edges

### ✅ Features Available

1. **Document Processing**
   - Upload and parse various formats (PDF, DOCX, TXT, etc.)
   - Automatic chunking and embedding generation
   - Metadata extraction

2. **Search Capabilities**
   - Semantic search using vector embeddings
   - Keyword search
   - Hybrid search combining both

3. **Chat Interface**
   - LLM-powered conversations
   - Context-aware responses
   - Document-based Q&A

4. **Knowledge Graphs**
   - Automatic entity extraction
   - Relationship mapping
   - Graph visualization

5. **Local LLM Support**
   - Ollama integration configured
   - Models loaded: llama3.2:3b, nomic-embed-text
   - No external API dependency

## Quick Start Usage

### 1. Access the Application
```bash
# Frontend UI
http://localhost:3000

# API Documentation
http://localhost:8000/docs
```

### 2. Login
Use the test credentials:
- Username: `testuser`
- Password: `testpassword123`

### 3. Upload Documents
1. Navigate to Documents section
2. Click "Upload Document"
3. Select files to process
4. Wait for processing completion

### 4. Search and Chat
1. Use the search bar for semantic search
2. Open chat interface for conversations
3. Ask questions about your documents

### 5. View Knowledge Graphs
1. Navigate to Graphs section
2. Explore automatically generated relationships
3. Click nodes for detailed information

## Maintenance Commands

### Service Management
```bash
# View all services
docker compose ps

# Restart a service
docker compose restart morphik

# View logs
docker compose logs -f morphik

# Stop all services
docker compose down

# Start all services
docker compose --profile ollama up -d
```

### Database Operations
```bash
# Access PostgreSQL
docker exec -it postgres psql -U morphik morphik_db

# Backup database
docker exec postgres pg_dump -U morphik morphik_db > backup.sql

# Restore database
docker exec -i postgres psql -U morphik morphik_db < backup.sql
```

### Ollama Management
```bash
# List models
docker exec ollama ollama list

# Pull new model
docker exec ollama ollama pull <model-name>

# Remove model
docker exec ollama ollama rm <model-name>
```

## Next Steps

### Recommended Actions
1. **Change default passwords** in production
2. **Configure SSL/TLS** for secure connections
3. **Set up monitoring** with Prometheus/Grafana
4. **Implement backup strategy** for data persistence
5. **Review security settings** in morphik.toml

### Optional Enhancements
1. **Add more Ollama models** for different use cases
2. **Configure external storage** (S3) for documents
3. **Set up email notifications** for job completion
4. **Implement custom document parsers**
5. **Create custom knowledge graph schemas**

## Troubleshooting

### Common Issues and Solutions

1. **Port conflicts**
   ```bash
   # Check what's using a port
   lsof -i :3000
   # Kill the process
   kill -9 <PID>
   ```

2. **Ollama connection errors**
   ```bash
   # Restart Ollama
   docker compose restart ollama
   # Reload models
   docker exec ollama ollama pull llama3.2:3b
   ```

3. **Database connection issues**
   ```bash
   # Check PostgreSQL status
   docker compose logs postgres
   # Restart database
   docker compose restart postgres
   ```

4. **UI build errors**
   ```bash
   # Rebuild UI service
   docker compose build --no-cache ui
   docker compose up -d ui
   ```

## Support Resources

- **Documentation**: See MORPHIK_ARCHITECTURE.md for system details
- **Deployment Guide**: See MORPHIK_DEPLOYMENT_GUIDE.md for production setup
- **Changelog**: See MORPHIK_CHANGELOG.md for version history
- **GitHub**: https://github.com/We-are-Humans-Corp/Morphik_local
- **Discord**: https://discord.gg/morphik

## Summary

Your Morphik instance is fully configured and operational with:
- ✅ All services running
- ✅ Authentication working
- ✅ Local LLM configured
- ✅ Database initialized
- ✅ UI accessible
- ✅ Test account created

You can now start using Morphik for document processing, search, and AI-powered interactions!