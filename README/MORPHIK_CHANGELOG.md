# Morphik Changelog

## [Current] - 2025-07-31

### Added
- Separated infrastructure setup for shared services (Ollama, Redis, PostgreSQL)
- New clean docker-compose configurations for stable and experimental versions
- Ability to run both versions simultaneously on different ports
- Automated Ollama model loading in experimental environment
- Shared network architecture for better service communication

### Fixed
- Worker connection to Ollama service in experimental environment
- File upload processing now completes successfully
- Network isolation issues between different docker-compose setups
- Model loading and embedding generation workflow

### Changed
- Restructured project to separate infrastructure from application code
- Experimental version now uses dedicated Ollama instance
- Improved docker network configuration for service discovery
- Updated ports: Experimental (UI: 3001, API: 8001), Stable (UI: 3000, API: 8000)

### Technical Details
- Fixed "Name or service not known" error for Ollama connection
- Worker now properly connects to Ollama at http://ollama:11434
- File processing status correctly updates from "processing" to "completed"
- Both llama3.2:3b and nomic-embed-text models loaded and working

## [0.2.1] - 2025-07-30

### Fixed
- Replaced all hardcoded api.morphik.ai URLs with localhost:8000
- Fixed UI to API connection issues (CORS and internal routing)
- Added INTERNAL_API_URL environment variable for server-side API calls
- Fixed bcrypt password hashing for user authentication
- Resolved 500 errors in chat due to missing document files

### Changed
- Updated all API endpoints in UI components to use environment variables
- Modified docker-compose.yml to include both NEXT_PUBLIC_API_URL and INTERNAL_API_URL
- Updated auth routes to handle both browser and server-side requests

### Configuration
- NEXT_PUBLIC_API_URL=http://localhost:8000 (for browser requests)
- INTERNAL_API_URL=http://morphik:8000 (for server-side requests)

## [0.2.0] - 2025-01-18

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