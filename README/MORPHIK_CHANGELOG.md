# Morphik Changelog

## [Current] - 2025-08-19

### Fixed
- Worker container connection to remote PostgreSQL (135.181.106.12)
- Docker entrypoint script now correctly handles remote services
- Removed duplicate local Redis and Ollama containers that were not being used
- Fixed PostgreSQL URI format conversion for asyncpg (postgresql+asyncpg:// -> postgresql://)

### Changed
- Created custom docker-entrypoint.sh that properly checks remote PostgreSQL connection
- Modified docker-compose.local.yml to use custom entrypoint via volume mount
- Optimized container architecture: only API, Worker, and UI run locally
- All heavy services (PostgreSQL, Redis, Ollama) now correctly use remote server

### Technical Details
- Problem: Worker container was trying to connect to local 'postgres' hostname instead of remote IP
- Solution: Custom entrypoint script that:
  - Extracts PostgreSQL host from POSTGRES_URI environment variable
  - Converts SQLAlchemy URI format to asyncpg format
  - Uses Python asyncpg to verify connection with proper timeout and retry logic
- Implementation: Volume mount docker-entrypoint.sh as /app/docker-entrypoint-custom.sh in worker service

## [Previous] - 2025-08-18

### Fixed
- Model filtering now correctly shows only available models based on API keys
- Removed duplicate model entries in UI (eliminated "Custom model" duplicates)
- User authentication system - corrected password hashing format
- Updated all documentation with correct login credentials
- Fixed morphik.toml to comment out models without API keys

### Added
- Smart model filtering based on available API keys in database
- New `create_user.py` script for user management
- `UserData.md` documentation file with complete authentication details
- Support for multiple user accounts (test@example.com, fedor@example.com)
- ModelSelectorHeader component for potential header placement

### Changed
- Model availability now determined by API keys stored in database (not env vars)
- Authentication now uses email as username (e.g., test@example.com)
- Password hashing uses SHA256 with salt format: {salt}${hash}
- Updated all README files with correct login credentials
- Disabled custom models endpoint to prevent duplicates
- Models endpoint now returns only genuinely available models

### Technical Improvements
- Backend `/models` endpoint filters based on database-stored API keys
- Ollama models always available (local, no key required)
- Removed redundant custom models loading in UI
- Improved model provider detection logic

### Documentation
- Created comprehensive UserData.md with authentication details
- Updated README files in both /README/ and /Test/Morphik_local/
- Added troubleshooting guide for authentication issues
- Corrected architecture description (hybrid local/remote setup)

## [Previous] - 2025-07-31

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
- Hybrid architecture: core services in Docker, shared resources on remote server
- Backend API and Worker running in local Docker containers
- PostgreSQL and Ollama hosted on remote server (135.181.106.12)
- UI runs locally via npm dev server (development) or Docker (production)
- Proper network configuration for local-remote communication
- Volume persistence for local data storage

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