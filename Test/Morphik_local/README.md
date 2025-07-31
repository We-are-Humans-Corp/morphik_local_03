# Morphik - Local Installation

This is a local installation of Morphik, an AI-native toolset for visually rich documents and multimodal data processing.

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- 8GB RAM minimum
- 20GB free disk space

### Installation
```bash
# 1. Clone the repository
git clone https://github.com/We-are-Humans-Corp/Morphik_local.git
cd Morphik_local

# 2. Set up environment
cp .env.example .env
# Edit .env with your configuration

# 3. Start all services
docker compose --profile ollama up -d

# 4. Load required models
docker exec -it ollama ollama pull llama3.2:3b
docker exec -it ollama ollama pull nomic-embed-text
```

### Access
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Default Login**: 
  - Username: `testuser`
  - Password: `testpassword123`

## Features

- 📄 **Document Processing**: Parse PDFs, DOCX, images, and more
- 🔍 **Multimodal Search**: Search across text and visual content
- 💬 **AI Chat**: Context-aware conversations with your documents
- 🕸️ **Knowledge Graphs**: Automatic entity and relationship extraction
- 🏠 **Local LLMs**: Run completely offline with Ollama
- 🔒 **Secure**: JWT authentication with proper password hashing

## Documentation

- [Architecture Overview](./MORPHIK_ARCHITECTURE.md) - System design and components
- [Setup Complete Guide](./MORPHIK_SETUP_COMPLETE.md) - Detailed setup verification
- [Deployment Guide](./MORPHIK_DEPLOYMENT_GUIDE.md) - Production deployment instructions
- [Changelog](./MORPHIK_CHANGELOG.md) - Version history and updates

## Services

| Service | Port | Description |
|---------|------|-------------|
| UI | 3000 | Next.js frontend application |
| API | 8000 | FastAPI backend server |
| PostgreSQL | 5432 | Database with pgvector extension |
| Redis | 6379 | Queue and cache |
| Ollama | 11434 | Local LLM inference |
| Worker | - | Background job processor |

## Configuration

Main configuration files:
- `.env` - Environment variables
- `morphik.toml` - Application settings
- `docker-compose.yml` - Service definitions

## Common Commands

```bash
# View service status
docker compose ps

# View logs
docker compose logs -f

# Restart a service
docker compose restart morphik

# Stop all services
docker compose down

# Remove all data (careful!)
docker compose down -v
```

## Development

### Project Structure
```
Morphik_local/
├── core/           # Core API and business logic
├── ee/             # Enterprise edition features
│   └── ui-component/  # Next.js frontend
├── worker/         # Background job processing
├── scripts/        # Utility scripts
└── docker-compose.yml
```

### Adding New Features
1. Create feature branch
2. Implement changes
3. Test locally
4. Submit pull request

## Troubleshooting

### Port Already in Use
```bash
lsof -i :3000  # Find process
kill -9 <PID>  # Kill process
```

### Ollama Connection Error
```bash
docker compose restart ollama
docker exec ollama ollama list
```

### Database Issues
```bash
docker compose logs postgres
docker compose restart postgres
```

## Support

- GitHub Issues: [Report bugs](https://github.com/We-are-Humans-Corp/Morphik_local/issues)
- Discord: [Join community](https://discord.gg/morphik)
- Documentation: [Official docs](https://morphik.ai/docs)

## License

Morphik Core is source-available under the Business Source License 1.1. See [LICENSE](./LICENSE) for details.

---

Built with ❤️ by the Morphik team