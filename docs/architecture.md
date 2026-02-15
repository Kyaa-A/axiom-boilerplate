# Architecture Overview

## System Layers

This boilerplate implements a clean, layered architecture optimized for AI-first applications.

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   UI Layer   │  │ State Layer  │  │   API Client     │  │
│  │  (shadcn/ui) │  │   (Zustand   │  │    (Axios)       │  │
│  │              │  │  TanStack Q) │  │                  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ▼
                    HTTP/REST API (JSON)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend API (FastAPI)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API Layer (v1 endpoints)                 │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Service Layer (Business Logic)              │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │         AI Orchestration (LangChain)           │  │  │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────────┐   │  │  │
│  │  │  │ Cerebras │ │ Voyage   │ │   Weaviate     │   │  │  │
│  │  │  │   LLM    │ │   AI     │ │ Vector Store │   │  │  │
│  │  │  └──────────┘ └──────────┘ └──────────────┘   │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        Repository Layer (Data Access)                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  PostgreSQL  │  │    Redis     │  │      Weaviate      │  │
│  │ (Structured) │  │(Cache/Queue) │  │(Vector Embeddings│  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Background Workers                         │
│                   (Celery + Redis)                           │
└─────────────────────────────────────────────────────────────┘
```

## Key Architectural Principles

### 1. Separation of Concerns

- **Frontend**: UI/UX only, no business logic
- **Backend API**: Orchestration and business logic
- **Services**: Isolated, single-responsibility modules
- **Repositories**: Database access abstraction
- **Workers**: Asynchronous task processing

### 2. AI Data Flow

**CRITICAL RULE**: Frontend NEVER accesses AI services directly.

```
User Request
    ↓
Frontend API Client
    ↓
Backend API Endpoint
    ↓
LangChain Orchestration Layer
    ↓
┌─────────────┬─────────────┬─────────────┐
│  Cerebras   │  Voyage AI  │   Weaviate    │
│    (LLM)    │ (Embeddings)│  (Vectors)  │
└─────────────┴─────────────┴─────────────┘
```

### 3. Database Strategy

**PostgreSQL** (Relational)
- User data
- Document metadata
- Application state
- Transactional data

**Weaviate** (Vector)
- Text embeddings
- Semantic search
- AI memory/context

**Why Separate?**
- Optimized for different access patterns
- Weaviate excels at similarity search
- PostgreSQL handles structured queries
- Independent scaling

### 4. State Management

**Frontend State**
- **Zustand**: UI state (sidebar, modals, theme)
- **TanStack Query**: Server state (API data, caching)

**Backend State**
- **PostgreSQL**: Persistent data
- **Redis**: Cache + session + queue
- **Weaviate**: Vector embeddings

## Layer Responsibilities

### Frontend Layer

**Location**: `frontend/`

**Responsibilities**:
- User interface rendering
- User input collection
- Client-side validation
- State management (UI + Server)
- API communication

**Does NOT**:
- Call AI services directly
- Contain business logic
- Access databases directly
- Process embeddings

### API Layer

**Location**: `backend/app/api/`

**Responsibilities**:
- HTTP request/response handling
- Input validation (Pydantic schemas)
- Authentication/authorization
- Route definitions
- Error handling

### Service Layer

**Location**: `backend/app/services/`

**Responsibilities**:
- Business logic implementation
- AI orchestration (LangChain)
- External service integration
- Complex computations
- Workflow coordination

### Repository Layer

**Location**: `backend/app/repositories/`

**Responsibilities**:
- Database queries
- Data persistence
- Transaction management
- Query optimization

### Worker Layer

**Location**: `backend/app/workers/`

**Responsibilities**:
- Background task execution
- Batch processing
- Scheduled jobs
- Long-running operations

## Request Flow Examples

### Example 1: RAG Query

```
1. User types question in frontend
2. Frontend calls POST /api/v1/ai/query
3. Backend API endpoint receives request
4. RAG Chain orchestrates:
   a. Generate query embedding (Voyage AI)
   b. Search similar vectors (Weaviate)
   c. Retrieve context from results
   d. Generate response (Cerebras LLM)
5. Response returned to frontend
6. Frontend displays result
```

### Example 2: Document Creation

```
1. User submits document via frontend
2. Frontend calls POST /api/v1/documents
3. Backend API endpoint:
   a. Validates input
   b. Saves to PostgreSQL (Repository)
   c. Triggers embedding generation
4. Embedding Chain:
   a. Generate embedding (Voyage AI)
   b. Store in Weaviate
   c. Update PostgreSQL with vector reference
5. Response returned with document ID
6. Frontend updates UI
```

### Example 3: Batch Processing

```
1. API endpoint queues batch task
2. Celery worker picks up task
3. Worker processes batch:
   a. Generate embeddings
   b. Store in Weaviate
   c. Update PostgreSQL
4. Task completion stored in Redis
5. Frontend polls for status or receives webhook
```

## Security Architecture

### Authentication Flow

```
User Login
    ↓
Supabase Auth
    ↓
JWT Token ← stored in frontend
    ↓
API Requests (Authorization: Bearer <token>)
    ↓
Backend validates JWT
    ↓
Access granted/denied
```

### API Security

- CORS configured for allowed origins
- JWT validation on protected routes
- Rate limiting (TODO: implement)
- Input validation via Pydantic
- SQL injection prevention (SQLAlchemy ORM)

## Scalability Considerations

### Horizontal Scaling

- **Frontend**: Deploy to CDN (Vercel)
- **Backend**: Multiple uvicorn instances behind load balancer
- **Workers**: Scale Celery workers independently
- **Databases**: Read replicas, connection pooling

### Vertical Scaling

- Adjust database pool sizes
- Increase worker concurrency
- Optimize query performance

### Caching Strategy

- Redis for frequently accessed data
- TanStack Query for frontend caching
- CDN for static assets

## Technology Choices

| Component | Technology | Why |
|-----------|-----------|-----|
| Frontend Framework | Next.js 14 | App Router, SSR, optimal DX |
| UI Library | shadcn/ui | Customizable, accessible components |
| UI State | Zustand | Lightweight, simple API |
| Server State | TanStack Query | Caching, invalidation, devtools |
| Backend Framework | FastAPI | Async, type safety, auto docs |
| ORM | SQLAlchemy | Async support, mature, flexible |
| Task Queue | Celery | Mature, reliable, distributed |
| LLM Provider | Cerebras | Fast inference, cost-effective |
| Embeddings | Voyage AI | High-quality embeddings |
| Vector DB | Weaviate | Scalable search, filtering, ecosystem |
| Cache/Queue | Redis | Speed, versatility, reliability |

## Deployment Architecture

### Development
- Docker Compose orchestrates all services
- Hot reload for frontend and backend
- Local databases

### Production
- **Frontend**: Vercel (or similar CDN)
- **Backend**: Azure App Service / Container Instances
- **Databases**: Managed services (Azure PostgreSQL, Weaviate Cloud)
- **Redis**: Azure Cache for Redis
- **Workers**: Separate container instances

## Next Steps

After setting up this boilerplate:

1. **Authorization**: Add role-based access control
2. **Rate Limiting**: Add request rate limits
3. **Monitoring**: Integrate logging/metrics (e.g., Sentry, Datadog)
4. **Testing**: Add unit and integration tests
5. **CI/CD**: Set up GitHub Actions workflows
6. **Documentation**: Add OpenAPI/Swagger docs
