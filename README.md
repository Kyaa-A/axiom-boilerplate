# AI Boilerplate - Production-Ready Full-Stack AI Application

A scalable, production-ready full-stack boilerplate for building AI-first applications with Next.js, FastAPI, and modern AI services.

> **🚀 Quick Start for New Projects**: Simply clone this repository to start a new project:
> ```bash
> git clone https://github.com/Kyaa-A/axiom-boilerplate.git your-project-name
> cd your-project-name
> ```

## 🎯 Project Goals

- **Clean Architecture**: Separation of concerns, SOLID principles
- **AI-First**: Built around LangChain orchestration
- **Scalable**: Ready for production deployment
- **Feature-Agnostic**: Foundation for any AI SaaS product
- **Portfolio-Grade**: Professional, well-documented codebase

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
│         React + TypeScript + TailwindCSS + shadcn        │
└─────────────────────────────────────────────────────────┘
                          ▼ HTTP/REST
┌─────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                      │
│              Python + SQLAlchemy + Celery                │
│  ┌────────────────────────────────────────────────────┐ │
│  │         AI Orchestration (LangChain)               │ │
│  │  Cerebras + Voyage AI + Qdrant                     │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          ▼
┌──────────────┬──────────────┬──────────────┬────────────┐
│  PostgreSQL  │    Redis     │   Qdrant     │   Celery   │
│ (Structured) │(Cache/Queue) │  (Vectors)   │ (Workers)  │
└──────────────┴──────────────┴──────────────┴────────────┘
```

## 📚 Documentation

- **[Architecture Overview](docs/architecture.md)**: System design, layers, data flow
- **[AI Stack Guide](docs/ai-stack.md)**: LangChain, Cerebras, Voyage AI, Qdrant

## 🛠️ Tech Stack

### Frontend
- **Next.js 14** (App Router)
- **React 18** + **TypeScript**
- **TailwindCSS** + **shadcn/ui**
- **Zustand** (UI state)
- **TanStack Query** (Server state)
- **React Hook Form** + **Zod**

### Backend
- **FastAPI** (Async Python)
- **SQLAlchemy** (ORM)
- **Celery** (Background tasks)
- **Redis** (Cache + Queue)

### AI & Data
- **LangChain** (Orchestration)
- **Cerebras** (LLM)
- **Voyage AI** (Embeddings)
- **Qdrant** (Vector DB)
- **PostgreSQL** (Relational DB)
- **Supabase** (Auth + Storage)

### DevOps
- **Docker** + **Docker Compose**
- **Azure** (Deployment)
- **Vercel** (Frontend hosting)

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 20+
- Git

### 1. Clone Repository

```bash
# Clone this boilerplate for your new project
git clone https://github.com/Kyaa-A/axiom-boilerplate.git your-project-name
cd your-project-name

# Remove the existing git history and initialize a new repository
rm -rf .git
git init
git add .
git commit -m "Initial commit from axiom-boilerplate"
```

### 2. Configure Environment

**Backend**:
```bash
cd backend
cp .env.example .env
# Edit .env with your API keys
```

**Frontend**:
```bash
cd frontend
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start Services

```bash
# Start all services with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Qdrant: http://localhost:6333

### 4. Initialize Database

```bash
# Run migrations (if using Alembic)
docker-compose exec backend alembic upgrade head
```

## 📁 Project Structure

```
axiom-boilerplate/
├── backend/
│   ├── app/
│   │   ├── core/               # Config, logging, database
│   │   ├── api/                # API endpoints
│   │   │   └── v1/
│   │   │       ├── endpoints/  # Route handlers
│   │   │       └── router.py   # Main router
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── repositories/       # Data access layer
│   │   ├── services/           # Business logic
│   │   │   └── ai/             # AI services
│   │   │       ├── llm/        # Cerebras client
│   │   │       ├── embeddings/ # Voyage AI client
│   │   │       ├── vector_store/ # Qdrant client
│   │   │       └── chains/     # LangChain orchestration
│   │   └── workers/            # Celery tasks
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── app/                    # Next.js App Router
│   ├── components/
│   │   ├── ui/                 # shadcn components
│   │   ├── features/           # Feature components
│   │   └── layout/             # Layout components
│   ├── lib/
│   │   ├── api/                # API client
│   │   ├── store/              # Zustand stores
│   │   └── utils/              # Utilities
│   ├── types/                  # TypeScript types
│   ├── hooks/                  # React hooks (TanStack Query)
│   ├── styles/                 # Global styles
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
│
├── infra/
│   ├── docker/                 # Docker configs
│   ├── scripts/                # Deployment scripts
│   └── configs/                # Infrastructure configs
│
├── docs/
│   ├── architecture.md         # Architecture guide
│   └── ai-stack.md             # AI stack guide
│
├── docker-compose.yml
└── README.md
```

## 🔑 Key Features

### AI-First Architecture

- **LangChain Orchestration**: All AI operations go through LangChain
- **RAG Ready**: Retrieval-Augmented Generation out of the box
- **Vector Search**: Semantic search with Qdrant
- **Clean Separation**: Frontend never calls AI services directly

### State Management

- **Zustand**: UI state (sidebar, modals, theme)
- **TanStack Query**: Server state (caching, invalidation)
- **PostgreSQL**: Persistent data
- **Redis**: Cache + session + queue

### Background Processing

- **Celery Workers**: Async task execution
- **Redis Queue**: Reliable job queue
- **Task Patterns**: Batch processing, scheduled jobs

### Developer Experience

- **Type Safety**: TypeScript + Pydantic
- **Auto Documentation**: OpenAPI/Swagger
- **Hot Reload**: Fast development cycle
- **Structured Logging**: JSON logs for production

## 🎨 API Examples

### RAG Query

```bash
POST http://localhost:8000/api/v1/ai/query
Content-Type: application/json

{
  "query": "What features does the product have?",
  "top_k": 5,
  "score_threshold": 0.7
}
```

### Create Document

```bash
POST http://localhost:8000/api/v1/documents
Content-Type: application/json

{
  "title": "Product Guide",
  "content": "Our product has features A, B, and C...",
  "source": "manual.pdf"
}
```

### Generate Text

```bash
POST http://localhost:8000/api/v1/ai/generate
Content-Type: application/json

{
  "prompt": "Explain quantum computing",
  "system_prompt": "You are a helpful physics teacher",
  "max_tokens": 500
}
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📦 Deployment

### Frontend (Vercel)

```bash
cd frontend
vercel deploy
```

### Backend (Azure)

```bash
# Build and push Docker image
docker build -t your-registry/backend:latest backend/
docker push your-registry/backend:latest

# Deploy to Azure Container Instances
az container create \
  --resource-group your-rg \
  --name ai-boilerplate-backend \
  --image your-registry/backend:latest \
  --environment-variables $(cat backend/.env)
```

## 🔒 Security

- JWT-based authentication via Supabase
- CORS configuration
- Input validation (Pydantic)
- SQL injection prevention (SQLAlchemy ORM)
- API key protection (environment variables)

## 🎯 Next Steps

After setting up:

1. **Implement Authentication**: Add Supabase auth integration
2. **Add Features**: Build on this foundation
3. **Set Up CI/CD**: GitHub Actions workflows
4. **Add Monitoring**: Integrate logging/metrics
5. **Write Tests**: Unit and integration tests
6. **Configure n8n**: External workflow automation

## 📝 Environment Variables

### Required Backend Variables

```bash
# AI Services
CEREBRAS_API_KEY=your-cerebras-key
VOYAGE_API_KEY=your-voyage-key

# Supabase
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db

# Security
SECRET_KEY=your-secret-key
```

### Required Frontend Variables

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

## 🤝 Contributing

This is a boilerplate template. Fork and customize for your needs.

## 📄 License

MIT License - Use freely for any project

## 🙋 Support

- Check documentation in `docs/`
- Review code comments
- Open issues for bugs

## ⭐ Features Checklist

- ✅ Clean architecture
- ✅ AI orchestration layer
- ✅ Vector database integration
- ✅ Background task processing
- ✅ State management (UI + Server)
- ✅ Docker setup
- ✅ Type safety (TypeScript + Pydantic)
- ✅ API documentation
- ✅ Environment configuration
- ⬜ Authentication (Supabase)
- ⬜ Authorization (RBAC)
- ⬜ Rate limiting
- ⬜ Monitoring & logging
- ⬜ Unit tests
- ⬜ Integration tests
- ⬜ CI/CD pipelines

---