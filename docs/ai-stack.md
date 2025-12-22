# AI Stack Documentation

## Overview

This boilerplate implements a production-ready AI stack with clear separation of responsibilities:

- **Cerebras**: Text generation (LLM)
- **Voyage AI**: Text embeddings
- **Qdrant**: Vector storage and similarity search
- **LangChain**: Orchestration layer

## Architecture Principles

### 1. Single Responsibility

Each AI service has ONE job:

```
┌──────────────────────────────────────────────────────┐
│ Cerebras                                             │
│ - Text generation                                    │
│ - Chat completions                                   │
│ - Streaming responses                                │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ Voyage AI                                            │
│ - Document embeddings (input_type="document")       │
│ - Query embeddings (input_type="query")             │
│ - Batch embedding generation                         │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ Qdrant                                               │
│ - Vector storage                                     │
│ - Similarity search                                  │
│ - Metadata filtering                                 │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ LangChain                                            │
│ - Orchestrates the above services                    │
│ - Implements RAG workflows                           │
│ - Chains complex AI operations                       │
└──────────────────────────────────────────────────────┘
```

### 2. No Direct AI Access from Frontend

**NEVER DO THIS**:
```typescript
// ❌ WRONG - Frontend calling AI directly
import { Cerebras } from '@cerebras/sdk';

const client = new Cerebras({ apiKey: process.env.CEREBRAS_KEY });
const response = await client.generate("Hello");
```

**ALWAYS DO THIS**:
```typescript
// ✅ CORRECT - Frontend calls backend API
import { apiClient } from '@/lib/api/client';

const { data } = await apiClient.ai.generate({ prompt: "Hello" });
```

### 3. Abstraction Layers

```
Frontend Request
      ↓
Backend API Endpoint (app/api/v1/endpoints/ai.py)
      ↓
LangChain Chain (app/services/ai/chains/base_chain.py)
      ↓
┌──────────────┬──────────────┬──────────────┐
│   LLM Client │  Embeddings  │ Vector Store │
│   (Cerebras) │ (Voyage AI)  │   (Qdrant)   │
└──────────────┴──────────────┴──────────────┘
```

## Service Details

### Cerebras (LLM)

**Purpose**: Generate natural language text

**Implementation**: `backend/app/services/ai/llm/cerebras_client.py`

**Features**:
- OpenAI-compatible API
- Streaming support
- Temperature control
- Token management

**Usage Example**:
```python
from app.services.ai.llm.cerebras_client import cerebras_client

# Generate text
response = await cerebras_client.generate(
    prompt="Explain quantum computing",
    system_prompt="You are a helpful physics teacher",
    max_tokens=500,
    temperature=0.7
)

# Stream text
async for chunk in cerebras_client.stream_generate(
    prompt="Write a story",
    max_tokens=1000
):
    print(chunk, end="")
```

**When to Use**:
- Text generation
- Chat completions
- Content creation
- Question answering (with or without context)

**When NOT to Use**:
- Generating embeddings (use Voyage AI)
- Vector search (use Qdrant)

### Voyage AI (Embeddings)

**Purpose**: Convert text to numerical vectors

**Implementation**: `backend/app/services/ai/embeddings/voyage_client.py`

**Features**:
- Document embeddings (for storage)
- Query embeddings (for search)
- Batch processing
- 1024-dimensional vectors (configurable)

**Usage Example**:
```python
from app.services.ai.embeddings.voyage_client import voyage_client

# Embed a document
doc_embedding = await voyage_client.embed_text(
    "This is a document about AI"
)

# Embed a search query
query_embedding = await voyage_client.embed_query(
    "What is AI?"
)

# Batch embed multiple documents
embeddings = await voyage_client.embed_batch(
    texts=["doc 1", "doc 2", "doc 3"],
    input_type="document"
)
```

**Input Types**:
- `"document"`: For text you want to store and search
- `"query"`: For search queries (optimized for retrieval)

**When to Use**:
- Before storing text in Qdrant
- Before searching Qdrant
- Semantic similarity calculations

**When NOT to Use**:
- Text generation (use Cerebras)
- Direct text search (use embeddings + Qdrant)

### Qdrant (Vector Database)

**Purpose**: Store and search vector embeddings

**Implementation**: `backend/app/services/ai/vector_store/qdrant_client.py`

**Features**:
- Cosine similarity search
- Metadata filtering
- Batch operations
- Collection management

**Usage Example**:
```python
from app.services.ai.vector_store.qdrant_store import qdrant_store

# Store embedding
vector_id = await qdrant_store.store_embedding(
    vector=embedding_vector,
    metadata={
        "text": "Original text",
        "source": "document.pdf",
        "created_at": "2024-01-01"
    }
)

# Search similar vectors
results = await qdrant_store.search_similar(
    query_vector=query_embedding,
    limit=5,
    score_threshold=0.7
)

# Results include metadata
for result in results:
    print(f"Score: {result['score']}")
    print(f"Text: {result['metadata']['text']}")
```

**When to Use**:
- Semantic search
- Finding similar documents
- RAG (Retrieval-Augmented Generation)
- Recommendation systems

**When NOT to Use**:
- Structured queries (use PostgreSQL)
- Exact text match (use PostgreSQL full-text search)
- Simple filtering (use PostgreSQL)

### LangChain (Orchestration)

**Purpose**: Combine AI services into workflows

**Implementation**: `backend/app/services/ai/chains/base_chain.py`

**Features**:
- RAG chain (retrieval + generation)
- Embedding chain (batch embedding + storage)
- Extensible base chain class

**Usage Example**:
```python
from app.services.ai.chains.base_chain import rag_chain

# Execute RAG workflow
result = await rag_chain.run(
    query="What is machine learning?",
    top_k=5,
    score_threshold=0.7
)

# Result contains:
# - response: Generated text from LLM
# - sources: Retrieved documents with scores
# - query: Original query
```

**Built-in Chains**:

1. **RAG Chain** (`RAGChain`)
   - Converts query to embedding
   - Searches Qdrant
   - Retrieves context
   - Generates response with Cerebras

2. **Embedding Chain** (`EmbeddingChain`)
   - Generates embeddings for documents
   - Stores in Qdrant
   - Returns vector IDs

**Creating Custom Chains**:
```python
from app.services.ai.chains.base_chain import BaseChain

class CustomChain(BaseChain):
    async def run(self, **kwargs):
        # Access services via:
        # - self.llm_client (Cerebras)
        # - self.embedding_client (Voyage AI)
        # - self.vector_store (Qdrant)

        # Implement your workflow
        pass
```

## RAG (Retrieval-Augmented Generation)

RAG is the core AI pattern in this boilerplate.

### Why RAG?

Without RAG:
```
User: "What's our refund policy?"
LLM: "I don't have specific information about your refund policy."
```

With RAG:
```
User: "What's our refund policy?"
System:
  1. Embeds query
  2. Finds relevant docs in Qdrant
  3. Passes docs as context to LLM
LLM: "According to your policy document, refunds are..."
```

### RAG Workflow

```
┌─────────────────────────────────────────────────────────┐
│ 1. User Query                                           │
│    "What features does the product have?"               │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Generate Query Embedding (Voyage AI)                │
│    [0.123, -0.456, 0.789, ...]                         │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Search Similar Vectors (Qdrant)                     │
│    Find top 5 most similar document embeddings          │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 4. Retrieve Context                                     │
│    - Doc 1: "The product has feature A..."             │
│    - Doc 2: "Feature B allows users to..."             │
│    - Doc 3: "Advanced features include C..."           │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 5. Generate Response (Cerebras)                        │
│    Prompt: "Based on the following context:\n          │
│             [Doc 1, Doc 2, Doc 3]\n                    │
│             Answer: What features does the product have?"│
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 6. Return Response + Sources                           │
│    "The product has features A, B, and C..."           │
│    Sources: [Doc 1 (score: 0.92), Doc 2 (0.88), ...]  │
└─────────────────────────────────────────────────────────┘
```

## Data Flow: Document to Vector

### Storing Documents

```python
# 1. User uploads/creates document
document_data = {
    "title": "Product Guide",
    "content": "Our product has features A, B, and C...",
    "source": "manual.pdf"
}

# 2. Store in PostgreSQL (structured data)
document = await document_repo.create(document_data)

# 3. Generate embedding
embedding = await voyage_client.embed_text(document.content)

# 4. Store in Qdrant (vector data)
vector_id = await qdrant_store.store_embedding(
    vector=embedding,
    metadata={
        "text": document.content,
        "title": document.title,
        "document_id": str(document.id)
    }
)

# 5. Link PostgreSQL record to Qdrant vector
await document_repo.update_vector_id(document.id, vector_id)
```

### Searching Documents

```python
# 1. User submits query
query = "What features does the product have?"

# 2. Generate query embedding
query_embedding = await voyage_client.embed_query(query)

# 3. Search Qdrant
results = await qdrant_store.search_similar(
    query_vector=query_embedding,
    limit=5,
    score_threshold=0.7
)

# 4. Extract context and generate response
context = "\n\n".join([r["metadata"]["text"] for r in results])
response = await cerebras_client.generate(
    prompt=f"Context:\n{context}\n\nQuestion: {query}"
)
```

## Best Practices

### 1. Always Use Abstractions

```python
# ❌ Don't instantiate clients directly
from cerebras import Cerebras
client = Cerebras(api_key="...")

# ✅ Use singleton instances
from app.services.ai.llm.cerebras_client import cerebras_client
response = await cerebras_client.generate(...)
```

### 2. Separate Concerns

```python
# ❌ Don't mix AI logic with API logic
@router.post("/query")
async def query(query: str):
    embedding = voyage_client.embed_query(query)
    results = qdrant_store.search(embedding)
    # ... more logic

# ✅ Use service layer
@router.post("/query")
async def query(query_data: QueryRequest):
    result = await rag_chain.run(
        query=query_data.query,
        top_k=query_data.top_k
    )
    return result
```

### 3. Handle Errors Gracefully

```python
try:
    response = await cerebras_client.generate(prompt)
except Exception as e:
    logger.error("LLM generation failed", error=str(e))
    # Fallback logic or user-friendly error
    raise HTTPException(status_code=500, detail="AI service unavailable")
```

### 4. Cache When Possible

```python
# Cache embeddings for frequently asked queries
cache_key = f"embedding:{hash(text)}"
embedding = await cache_client.get(cache_key)

if not embedding:
    embedding = await voyage_client.embed_text(text)
    await cache_client.set(cache_key, embedding, expire=3600)
```

### 5. Use Background Tasks for Heavy Operations

```python
# Don't block API responses
from app.workers.tasks import generate_embeddings_batch

@router.post("/documents/bulk")
async def bulk_upload(documents: List[DocumentCreate]):
    # Store documents quickly
    stored = await document_repo.create_batch(documents)

    # Process embeddings in background
    task = generate_embeddings_batch.delay([
        {"id": d.id, "text": d.content} for d in stored
    ])

    return {"message": "Processing", "task_id": task.id}
```

## Configuration

All AI services are configured via environment variables:

```bash
# Cerebras
CEREBRAS_API_KEY=your-key
CEREBRAS_MODEL=llama3.1-8b
CEREBRAS_MAX_TOKENS=1024
CEREBRAS_TEMPERATURE=0.7

# Voyage AI
VOYAGE_API_KEY=your-key
VOYAGE_MODEL=voyage-2
VOYAGE_EMBEDDING_DIMENSION=1024

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=embeddings
```

## Testing AI Services

```python
# Test Cerebras
async def test_llm():
    response = await cerebras_client.generate(
        prompt="Say hello",
        max_tokens=10
    )
    assert "hello" in response.lower()

# Test Voyage AI
async def test_embeddings():
    embedding = await voyage_client.embed_text("test")
    assert len(embedding) == 1024  # Default dimension

# Test Qdrant
async def test_vector_store():
    await qdrant_store.ensure_collection()
    vector_id = await qdrant_store.store_embedding(
        vector=[0.1] * 1024,
        metadata={"test": "data"}
    )
    assert vector_id is not None
```

## Cost Optimization

1. **Cache embeddings**: Same text = same embedding
2. **Batch operations**: Use `embed_batch()` for multiple texts
3. **Adjust top_k**: Don't retrieve more results than needed
4. **Set score_threshold**: Filter low-quality matches
5. **Stream responses**: Use streaming for better UX with long generations

## Extending the AI Stack

### Adding a New AI Provider

1. Create client in `app/services/ai/<category>/<provider>_client.py`
2. Follow single-responsibility pattern
3. Create singleton instance
4. Use in chains or services
5. Update environment configuration

### Creating Custom Chains

See `app/services/ai/chains/base_chain.py` for examples.

Common chain patterns:
- **Summarization Chain**: Embed docs → search → summarize
- **Classification Chain**: Embed text → compare to categories
- **Translation Chain**: Translate → embed → store
- **Multi-step Chain**: Generate → validate → refine

## Monitoring AI Services

Track these metrics:
- Token usage (Cerebras)
- Embedding generation count (Voyage AI)
- Vector search latency (Qdrant)
- Cache hit rate (Redis)
- RAG response time (end-to-end)

## Troubleshooting

**Issue**: Embeddings not found in Qdrant
- Check if collection exists: `await qdrant_store.ensure_collection()`
- Verify embedding dimension matches collection config

**Issue**: Poor RAG results
- Increase `top_k` parameter
- Lower `score_threshold`
- Check embedding quality (same model for doc and query?)
- Verify document chunking strategy

**Issue**: Slow responses
- Enable caching for embeddings
- Use streaming for LLM responses
- Batch embed operations
- Check Qdrant index settings
