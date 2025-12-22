"""
Qdrant vector database client.
This is the ONLY interface for vector storage and retrieval in the application.
"""
from typing import List, Dict, Any, Optional
from uuid import uuid4

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    SearchRequest,
)

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class QdrantVectorStore:
    """
    Async Qdrant vector store client.

    Responsibilities:
    - Vector storage and retrieval
    - Semantic search
    - Collection management
    """

    def __init__(self):
        self.client = AsyncQdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            api_key=settings.QDRANT_API_KEY,
        )
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.vector_dimension = settings.VOYAGE_EMBEDDING_DIMENSION

    async def ensure_collection(self) -> None:
        """Create collection if it doesn't exist."""
        try:
            collections = await self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.collection_name not in collection_names:
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_dimension,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(
                    "Collection created",
                    collection=self.collection_name,
                    dimension=self.vector_dimension,
                )
            else:
                logger.info(
                    "Collection exists",
                    collection=self.collection_name,
                )

        except Exception as e:
            logger.error("Collection setup failed", error=str(e))
            raise

    async def store_embedding(
        self,
        vector: List[float],
        metadata: Dict[str, Any],
        point_id: Optional[str] = None,
    ) -> str:
        """
        Store a single embedding with metadata.

        Args:
            vector: Embedding vector
            metadata: Associated metadata
            point_id: Optional custom ID (UUID generated if not provided)

        Returns:
            Point ID
        """
        try:
            point_id = point_id or str(uuid4())

            point = PointStruct(
                id=point_id,
                vector=vector,
                payload=metadata,
            )

            await self.client.upsert(
                collection_name=self.collection_name,
                points=[point],
            )

            logger.info("Embedding stored", point_id=point_id)
            return point_id

        except Exception as e:
            logger.error("Embedding storage failed", error=str(e))
            raise

    async def store_batch(
        self,
        vectors: List[List[float]],
        metadata_list: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Store multiple embeddings with metadata.

        Args:
            vectors: List of embedding vectors
            metadata_list: List of metadata dicts

        Returns:
            List of point IDs
        """
        try:
            if len(vectors) != len(metadata_list):
                raise ValueError("Vectors and metadata lists must have same length")

            points = []
            point_ids = []

            for vector, metadata in zip(vectors, metadata_list):
                point_id = str(uuid4())
                point_ids.append(point_id)

                points.append(
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=metadata,
                    )
                )

            await self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

            logger.info("Batch embeddings stored", count=len(points))
            return point_ids

        except Exception as e:
            logger.error("Batch storage failed", error=str(e))
            raise

    async def search_similar(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.7,
        filter_conditions: Optional[Filter] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.

        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            filter_conditions: Optional metadata filters

        Returns:
            List of search results with metadata and scores
        """
        try:
            results = await self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=filter_conditions,
            )

            formatted_results = [
                {
                    "id": result.id,
                    "score": result.score,
                    "metadata": result.payload,
                }
                for result in results
            ]

            logger.info("Vector search completed", results_count=len(formatted_results))
            return formatted_results

        except Exception as e:
            logger.error("Vector search failed", error=str(e))
            raise

    async def delete_by_id(self, point_id: str) -> bool:
        """Delete a vector by ID."""
        try:
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=[point_id],
            )
            logger.info("Vector deleted", point_id=point_id)
            return True

        except Exception as e:
            logger.error("Vector deletion failed", error=str(e))
            return False


# Global client instance
qdrant_store = QdrantVectorStore()
