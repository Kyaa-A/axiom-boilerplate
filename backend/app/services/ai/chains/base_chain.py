"""
LangChain base chain setup.
This orchestrates AI services (Cerebras LLM + Voyage embeddings + Qdrant vectors).
"""
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from app.services.ai.llm.cerebras_client import cerebras_client
from app.services.ai.embeddings.voyage_client import voyage_client
from app.services.ai.vector_store.qdrant_client import qdrant_store
from app.core.logging import get_logger

logger = get_logger(__name__)


class BaseChain(ABC):
    """
    Base class for LangChain-style chains.

    Provides access to:
    - LLM generation (Cerebras)
    - Embeddings (Voyage AI)
    - Vector storage (Qdrant)
    """

    def __init__(self):
        self.llm_client = cerebras_client
        self.embedding_client = voyage_client
        self.vector_store = qdrant_store
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    async def run(self, **kwargs) -> Any:
        """Execute the chain logic."""
        pass


class RAGChain(BaseChain):
    """
    Retrieval-Augmented Generation chain.

    Workflow:
    1. Convert user query to embedding (Voyage AI)
    2. Search similar vectors (Qdrant)
    3. Retrieve context from results
    4. Generate response with context (Cerebras)
    """

    async def run(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.7,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute RAG workflow.

        Args:
            query: User query
            top_k: Number of relevant documents to retrieve
            score_threshold: Minimum similarity score
            system_prompt: Optional system prompt for LLM

        Returns:
            Generated response with sources
        """
        try:
            # Step 1: Generate query embedding
            self.logger.info("Generating query embedding")
            query_embedding = await self.embedding_client.embed_query(query)

            # Step 2: Search similar vectors
            self.logger.info("Searching vector store")
            search_results = await self.vector_store.search_similar(
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=score_threshold,
            )

            # Step 3: Extract context from results
            context_parts = []
            sources = []

            for result in search_results:
                metadata = result["metadata"]
                context_parts.append(metadata.get("text", ""))
                sources.append(
                    {
                        "id": result["id"],
                        "score": result["score"],
                        "metadata": metadata,
                    }
                )

            context = "\n\n".join(context_parts)

            # Step 4: Generate response with context
            self.logger.info("Generating LLM response")
            augmented_prompt = f"""Context information:
{context}

User question: {query}

Please answer the question based on the provided context."""

            response = await self.llm_client.generate(
                prompt=augmented_prompt,
                system_prompt=system_prompt,
            )

            return {
                "response": response,
                "sources": sources,
                "query": query,
            }

        except Exception as e:
            self.logger.error("RAG chain failed", error=str(e))
            raise


class EmbeddingChain(BaseChain):
    """
    Chain for embedding and storing documents.

    Workflow:
    1. Generate embeddings for documents (Voyage AI)
    2. Store in vector database (Qdrant)
    """

    async def run(
        self,
        documents: List[Dict[str, Any]],
        text_field: str = "text",
    ) -> List[str]:
        """
        Embed and store documents.

        Args:
            documents: List of documents with text and metadata
            text_field: Field name containing text to embed

        Returns:
            List of vector IDs
        """
        try:
            # Extract texts for embedding
            texts = [doc[text_field] for doc in documents]

            # Generate embeddings
            self.logger.info("Generating embeddings", count=len(texts))
            embeddings = await self.embedding_client.embed_batch(texts)

            # Store in vector database
            self.logger.info("Storing embeddings in vector store")
            vector_ids = await self.vector_store.store_batch(
                vectors=embeddings,
                metadata_list=documents,
            )

            self.logger.info("Documents embedded and stored", count=len(vector_ids))
            return vector_ids

        except Exception as e:
            self.logger.error("Embedding chain failed", error=str(e))
            raise


# Global chain instances
rag_chain = RAGChain()
embedding_chain = EmbeddingChain()
