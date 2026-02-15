"""
Weaviate vector database client.
This is the ONLY interface for vector storage and retrieval in the application.
"""
import asyncio
import json
from typing import List, Dict, Any, Optional
from uuid import uuid4

import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class WeaviateVectorStore:
    """
    Async Weaviate vector store client.

    Responsibilities:
    - Vector storage and retrieval
    - Semantic search
    - Collection (class) management
    """

    def __init__(self):
        self.base_url = settings.WEAVIATE_URL.rstrip("/")
        self.api_key = settings.WEAVIATE_API_KEY
        self.class_name = settings.WEAVIATE_CLASS_NAME
        self.vector_dimension = settings.VOYAGE_EMBEDDING_DIMENSION
        self.timeout_seconds = settings.WEAVIATE_TIMEOUT_SECONDS

        self._class_ready = False
        self._class_lock = asyncio.Lock()

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _validate_dimension(self, vector: List[float]) -> None:
        if len(vector) != self.vector_dimension:
            raise ValueError(
                f"Invalid embedding dimension: expected {self.vector_dimension}, got {len(vector)}"
            )

    async def _request(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.request(
                method=method,
                url=f"{self.base_url}{path}",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            if not response.content:
                return {}
            return response.json()

    async def _ensure_collection_once(self) -> None:
        if self._class_ready:
            return

        async with self._class_lock:
            if self._class_ready:
                return
            await self.ensure_collection()
            self._class_ready = True

    async def ensure_collection(self) -> None:
        """Create class if it doesn't exist."""
        try:
            schema = await self._request("GET", "/v1/schema")
            classes = schema.get("classes", [])
            existing_class_names = [item.get("class") for item in classes]

            if self.class_name not in existing_class_names:
                await self._request(
                    "POST",
                    "/v1/schema",
                    payload={
                        "class": self.class_name,
                        "description": "Embedding storage for semantic search",
                        "vectorizer": "none",
                        "vectorIndexType": "hnsw",
                        "vectorIndexConfig": {"distance": "cosine"},
                        "properties": [
                            {
                                "name": "metadata_json",
                                "dataType": ["text"],
                                "description": "Serialized metadata payload",
                            }
                        ],
                    },
                )
                logger.info(
                    "Class created",
                    class_name=self.class_name,
                    dimension=self.vector_dimension,
                )
            else:
                logger.info("Class exists", class_name=self.class_name)

        except Exception as e:
            logger.error("Class setup failed", error=str(e))
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
            await self._ensure_collection_once()
            self._validate_dimension(vector)

            point_id = point_id or str(uuid4())
            await self._request(
                "POST",
                "/v1/objects",
                payload={
                    "class": self.class_name,
                    "id": point_id,
                    "properties": {
                        "metadata_json": json.dumps(metadata),
                    },
                    "vector": vector,
                },
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
            await self._ensure_collection_once()

            if len(vectors) != len(metadata_list):
                raise ValueError("Vectors and metadata lists must have same length")

            point_ids: List[str] = []
            objects: List[Dict[str, Any]] = []

            for vector, metadata in zip(vectors, metadata_list):
                self._validate_dimension(vector)
                point_id = str(uuid4())
                point_ids.append(point_id)
                objects.append(
                    {
                        "class": self.class_name,
                        "id": point_id,
                        "properties": {
                            "metadata_json": json.dumps(metadata),
                        },
                        "vector": vector,
                    }
                )

            response = await self._request(
                "POST",
                "/v1/batch/objects",
                payload={"objects": objects},
            )
            if response.get("errors"):
                raise RuntimeError(str(response["errors"]))

            for item in response.get("objects", []):
                errors = (
                    item.get("result", {})
                    .get("errors", {})
                    .get("error", [])
                )
                if errors:
                    raise RuntimeError(str(errors))

            logger.info("Batch embeddings stored", count=len(point_ids))
            return point_ids

        except Exception as e:
            logger.error("Batch storage failed", error=str(e))
            raise

    async def search_similar(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.7,
        filter_conditions: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.

        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            filter_conditions: Optional metadata filters (not yet implemented)

        Returns:
            List of search results with metadata and scores
        """
        try:
            await self._ensure_collection_once()
            self._validate_dimension(query_vector)

            if filter_conditions:
                logger.warning("Filter conditions are currently ignored in Weaviate search")

            vector_str = ", ".join(str(value) for value in query_vector)
            query = f"""
            {{
              Get {{
                {self.class_name}(
                  nearVector: {{ vector: [{vector_str}] }}
                  limit: {limit}
                ) {{
                  metadata_json
                  _additional {{
                    id
                    certainty
                    distance
                  }}
                }}
              }}
            }}
            """

            response = await self._request("POST", "/v1/graphql", payload={"query": query})
            if response.get("errors"):
                raise RuntimeError(str(response["errors"]))

            results = response.get("data", {}).get("Get", {}).get(self.class_name, [])

            formatted_results: List[Dict[str, Any]] = []
            for result in results:
                metadata_raw = result.get("metadata_json", "{}")
                metadata: Dict[str, Any]

                if isinstance(metadata_raw, str):
                    try:
                        metadata = json.loads(metadata_raw)
                    except json.JSONDecodeError:
                        metadata = {"raw_metadata": metadata_raw}
                elif isinstance(metadata_raw, dict):
                    metadata = metadata_raw
                else:
                    metadata = {}

                additional = result.get("_additional", {})
                certainty = additional.get("certainty")
                if certainty is not None:
                    score = float(certainty)
                else:
                    distance = float(additional.get("distance", 1.0))
                    score = max(0.0, 1.0 - distance)

                if score >= score_threshold:
                    formatted_results.append(
                        {
                            "id": additional.get("id"),
                            "score": score,
                            "metadata": metadata,
                        }
                    )

            logger.info("Vector search completed", results_count=len(formatted_results))
            return formatted_results

        except Exception as e:
            logger.error("Vector search failed", error=str(e))
            raise

    async def delete_by_id(self, point_id: str) -> bool:
        """Delete a vector by ID."""
        try:
            await self._ensure_collection_once()
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.delete(
                    f"{self.base_url}/v1/objects/{point_id}",
                    headers=self._headers(),
                )

            if response.status_code in (200, 204):
                logger.info("Vector deleted", point_id=point_id)
                return True

            if response.status_code == 404:
                logger.warning("Vector not found", point_id=point_id)
                return False

            response.raise_for_status()
            return False

        except Exception as e:
            logger.error("Vector deletion failed", error=str(e))
            return False


# Global client instance
weaviate_store = WeaviateVectorStore()
