# Morphik Changelog

## [0.4.8] - 2025-08-21

### Fixed
- Critical fix for chat history persistence in PostgreSQL
- Resolved timestamp type casting error preventing chats from being saved
- Fixed `upsert_chat_history` method to use `CURRENT_TIMESTAMP` instead of text casting

### Changed
- Database layer now correctly handles timestamp fields for chat history
- Chat sessions properly persist across user sessions

## [0.4.7] - 2025-08-20

### Added
- Force update UI script (force_update_ui.sh) for complete UI refresh
- Morphik UI diagnostic script (morphik_ui_diagnostic.sh) for system health checks
- New modern chat interface with sidebar chat history
- Improved UI layout with "Let's dive into your knowledge" welcome message
- Chat history functionality imported from upstream Morphik repository

### Fixed
- Removed duplicate UI installation in /Morphik_local/Morphik_local directory
- Resolved UI version conflicts between 0.4.1 and 0.4.7
- Fixed Docker cache issues preventing UI updates
- Corrected UI routing to use new version consistently

### Changed
- UI updated from version 0.4.1 to 0.4.7
- Migrated to single UI location in Test/Morphik_local
- Improved Docker build process with proper cache management
- Enhanced chat interface with better user experience

### Infrastructure
- Cleaned up 18.39GB of Docker cache
- Optimized container build process
- Removed redundant UI components

## [Current] - 2025-07-30

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