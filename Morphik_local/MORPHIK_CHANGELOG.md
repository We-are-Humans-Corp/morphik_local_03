# Morphik Changelog

## [Current] - 2025-01-18

### Added
- Complete Docker Compose setup with all services
- UI service integration with Next.js frontend
- JWT-based authentication system with SHA256+salt password hashing
- Support for multiple LLM providers (OpenAI, Anthropic, Google, Ollama)
- Local Ollama integration for offline LLM usage
- Redis queue for background job processing
- PostgreSQL with pgvector for semantic search
- Multimodal document processing capabilities
- Knowledge graph generation
- Cache-augmented generation for improved performance

### Fixed
- Authentication datetime timezone issues (UTC consistency)
- ESLint build errors in UI component (unescaped apostrophes)
- Database query parameter mismatches in auth routes
- Docker Compose rebuild behavior with proper service dependencies
- Model registration and API endpoint mappings

### Configuration
- Added comprehensive morphik.toml configuration
- Environment variables properly configured
- JWT secret key implementation
- Model mappings for various providers
- Ollama models loaded: llama3.2:3b, nomic-embed-text

### Security
- Implemented proper password hashing with SHA256 + salt
- JWT token-based authentication
- Role-based access control (RBAC) foundation
- Secure session management with Redis

### Infrastructure
- All services running in Docker containers
- Proper port mappings and network configuration
- Volume persistence for data
- Health checks for service monitoring

## Migration Notes

### From Previous Versions
If you had an existing installation, ensure you:
1. Update your `.env` file with the new required variables
2. Run database migrations if upgrading from older versions
3. Rebuild all Docker images: `docker compose build --no-cache`
4. Load required Ollama models: `docker exec -it ollama ollama pull llama3.2:3b`

### Breaking Changes
- Authentication system completely overhauled
- New password hashing mechanism (SHA256 + salt)
- JWT token structure updated
- API endpoints restructured

## Known Issues
- None currently identified in this deployment

## Next Steps
- Implement additional authentication providers
- Add more comprehensive logging
- Enhance monitoring capabilities
- Expand model provider support