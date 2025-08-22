# Morphik Changelog

## [0.4.9] - 2025-08-22

### Major Update - UI Migration & Authentication System

### Added
- **Standalone Authentication Service**
  - Created separate auth-service on port 8080 with simple HTML pages
  - Implemented clean registration and login pages without framework dependencies
  - Added redirect mechanism for token transfer between domains
  - Python HTTP server for serving auth pages

- **Cross-Domain Authentication**
  - Implemented `/api/auth/callback` endpoint for secure token transfer
  - Added localStorage synchronization between ports 8080 and 3000
  - Cookie-based session management with 24-hour expiration

- **User Experience Improvements**
  - Removed duplicate user profile from header (kept only sidebar profile)
  - Fixed username display to show actual logged-in user instead of defaults
  - Added debug page for authentication troubleshooting

### Changed
- **UI Updated to Official Morphik v0.4.7**
  - Successfully migrated from v0.4.2 to official v0.4.7
  - Preserved all custom configurations from morphik.toml
  - Maintained connection to remote PostgreSQL (135.181.106.12)
  
- **Authentication Flow**
  - Moved from integrated React auth to standalone HTML service
  - Simplified login/logout process with clear redirects
  - Removed built-in /login and /register pages from main UI

### Fixed
- **PostgreSQL Integration**
  - Fixed Worker service compatibility with remote database
  - Resolved UUID/Integer type mismatch in users table
  - Corrected auth.py to work with PostgreSQL SERIAL auto-increment

- **UI Context & State Management**
  - Fixed userProfile loading from localStorage
  - Corrected morphik-context.tsx to properly handle user data
  - Resolved middleware redirects for unauthorized access

### Technical Details
- **Architecture**:
  - Auth Service: `localhost:8080` (HTML/JS)
  - UI Service: `localhost:3000` (Next.js)
  - API Service: `localhost:8000` (FastAPI)
  - Database: `135.181.106.12:5432` (PostgreSQL)

- **Security**:
  - JWT tokens with 7-day expiration
  - SHA256 + salt password hashing
  - Secure cross-domain token transfer
  - httpOnly cookies for session management

### Migration Guide
See [UI Update Guide](./README/UI_UPDATE_GUIDE.md) for detailed instructions on updating UI while preserving authentication.

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