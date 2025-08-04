# Morphik Architecture Overview

## Table of Contents
1. [System Overview](#system-overview)
2. [Core Components](#core-components)
3. [Data Flow](#data-flow)
4. [Security Architecture](#security-architecture)
5. [Deployment Architecture](#deployment-architecture)
6. [Technology Stack](#technology-stack)

## System Overview

Morphik is designed as a microservices-based architecture with clear separation of concerns between different components. The platform follows a modular approach allowing for scalability and maintainability.

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Frontend (Next.js)                         │
│                                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │   Chat   │ │Documents │ │  Search  │ │  Graphs  │ │ Settings │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │ HTTP/WebSocket
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         API Gateway (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │Auth Router   │  │Document API  │  │Chat API      │              │
│  │/auth/*       │  │/documents/*  │  │/query        │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
        ┌─────────────────────────┴─────────────────────────┐
        ▼                         ▼                         ▼
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│  PostgreSQL  │         │    Redis     │         │   Storage    │
│   pgvector   │         │    Queue     │         │  Local/S3    │
└──────────────┘         └──────────────┘         └──────────────┘
        │                         │                         │
        └─────────────────────────┴─────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Worker Services                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  Ingestion   │  │  Embedding   │  │  Workflow    │              │
│  │   Worker     │  │   Worker     │  │   Worker     │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Frontend Layer
- **Technology**: Next.js 14, React 18, TypeScript
- **UI Framework**: TailwindCSS, shadcn/ui
- **State Management**: React Context API
- **Real-time**: WebSocket connections for chat

### 2. API Layer
- **Framework**: FastAPI with async support
- **Authentication**: JWT-based with middleware
- **Validation**: Pydantic models
- **Documentation**: Auto-generated OpenAPI/Swagger

### 3. Database Layer
- **Primary DB**: PostgreSQL with pgvector extension
- **Vector Store**: pgvector for semantic search
- **Queue**: Redis for task distribution
- **Cache**: Redis for session management

### 4. Processing Layer
- **Document Parser**: Unstructured library, custom parsers
- **Embedding Engine**: Multiple providers (OpenAI, Ollama, etc.)
- **LLM Integration**: LiteLLM for unified interface
- **Knowledge Graph**: Custom graph builder with entity resolution

### 5. Storage Layer
- **Local Storage**: File system for development
- **Cloud Storage**: S3-compatible for production
- **Document Store**: Chunked storage with metadata

## Data Flow

### Document Ingestion Flow
```
1. User uploads document → API
2. API validates and stores file → Storage
3. API creates ingestion job → Redis Queue
4. Worker picks up job → Parse document
5. Worker chunks document → Generate embeddings
6. Worker stores chunks → PostgreSQL + pgvector
7. Worker updates status → Database
8. User receives notification → WebSocket/Polling
```

### Query Processing Flow
```
1. User sends query → API
2. API generates query embedding → Embedding Service
3. API performs vector search → pgvector
4. API applies reranking → Reranker Model
5. API retrieves chunks → Database
6. API builds context → LLM Service
7. LLM generates response → Streaming/Batch
8. API returns response → User
```

### Knowledge Graph Flow
```
1. Document chunks analyzed → Entity Extraction
2. Entities identified → NER Model
3. Relationships extracted → Relationship Model
4. Graph nodes created → PostgreSQL
5. Graph edges established → PostgreSQL
6. Graph indexed → Vector embeddings
7. Graph queryable → Cypher-like queries
```

## Security Architecture

### Authentication & Authorization
- **Method**: JWT tokens with refresh mechanism
- **Password**: SHA256 hashing with salt
- **Sessions**: Redis-backed session management
- **Permissions**: Role-based access control (RBAC)

### API Security
- **Rate Limiting**: Per-user and per-endpoint limits
- **Input Validation**: Pydantic models with strict validation
- **CORS**: Configurable origin policies
- **Headers**: Security headers (HSTS, CSP, etc.)

### Data Security
- **Encryption at Rest**: Database encryption
- **Encryption in Transit**: TLS 1.3
- **File Scanning**: Malware detection on uploads
- **Access Control**: Document-level permissions

## Deployment Architecture

### Docker Compose Stack
```yaml
services:
  morphik:       # Main API service
  worker:        # Background job processor
  postgres:      # Database with pgvector
  redis:         # Queue and cache
  ollama:        # Local LLM (optional)
  ui:            # Frontend application
```

### Scalability Considerations
- **Horizontal Scaling**: API and workers can scale independently
- **Load Balancing**: Nginx or cloud load balancers
- **Database Pooling**: Connection pooling for PostgreSQL
- **Caching Strategy**: Multi-level caching (Redis, CDN)

### High Availability
- **Database**: PostgreSQL replication
- **Queue**: Redis Sentinel for failover
- **Storage**: S3 with multi-region replication
- **API**: Multiple instances behind load balancer

## Technology Stack

### Backend Technologies
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **ORM**: SQLAlchemy (async)
- **Task Queue**: ARQ (Redis-based)
- **AI/ML**: LiteLLM, Sentence Transformers, LlamaIndex

### Frontend Technologies
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **Components**: shadcn/ui
- **State**: React Context + Hooks

### Infrastructure
- **Container**: Docker
- **Orchestration**: Docker Compose / Kubernetes
- **Reverse Proxy**: Nginx
- **Monitoring**: OpenTelemetry compatible
- **CI/CD**: GitHub Actions ready

### AI/ML Stack
- **LLM Providers**: OpenAI, Anthropic, Google, Ollama
- **Embeddings**: OpenAI, Sentence Transformers, Ollama
- **Vector DB**: pgvector
- **Reranking**: FlagEmbedding
- **Vision**: ColPali for multimodal search

## Performance Optimizations

### Caching Strategy
1. **Redis Cache**: Session data, frequently accessed metadata
2. **Vector Cache**: Pre-computed embeddings
3. **LLM Cache**: Cache-augmented generation for documents
4. **CDN**: Static assets and frontend

### Database Optimizations
1. **Connection Pooling**: Async connection management
2. **Index Strategy**: Optimized for vector and metadata queries
3. **Partitioning**: Time-based partitioning for logs
4. **Query Optimization**: Prepared statements and batch operations

### Processing Optimizations
1. **Batch Processing**: Bulk document operations
2. **Async Operations**: Non-blocking I/O throughout
3. **Worker Pools**: Dedicated workers for different tasks
4. **Resource Limits**: Memory and CPU constraints per worker

## Monitoring and Observability

### Metrics Collection
- **Application Metrics**: Request rates, response times
- **System Metrics**: CPU, memory, disk usage
- **Business Metrics**: Documents processed, queries handled

### Logging Strategy
- **Structured Logging**: JSON format for easy parsing
- **Log Levels**: Configurable per component
- **Log Aggregation**: Centralized log management

### Tracing
- **Distributed Tracing**: OpenTelemetry integration
- **Request Tracking**: End-to-end request tracing
- **Performance Profiling**: Bottleneck identification

## Future Architecture Considerations

### Planned Enhancements
1. **GraphQL API**: Alternative to REST for complex queries
2. **Event Sourcing**: Full audit trail of all operations
3. **Multi-Region**: Geographic distribution for lower latency
4. **Federation**: Multi-instance coordination

### Extensibility Points
1. **Plugin System**: Custom document processors
2. **Webhook Integration**: External system notifications
3. **Custom Models**: Bring your own AI models
4. **API Extensions**: Custom endpoints for specific use cases