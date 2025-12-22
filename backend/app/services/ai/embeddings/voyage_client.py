"""
Voyage AI embeddings client.
This is the ONLY interface for generating embeddings in the application.
"""
from typing import List
import voyageai

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class VoyageClient:
    """
    Voyage AI embeddings client.

    Responsibilities:
    - Text embedding generation
    - Batch embedding processing
    - Dimension management
    """

    def __init__(self):
        self.client = voyageai.Client(api_key=settings.VOYAGE_API_KEY)
        self.model = settings.VOYAGE_MODEL
        self.dimension = settings.VOYAGE_EMBEDDING_DIMENSION

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            result = self.client.embed(
                texts=[text],
                model=self.model,
                input_type="document"
            )

            embedding = result.embeddings[0]
            logger.info(
                "Embedding generated",
                model=self.model,
                dimension=len(embedding),
            )
            return embedding

        except Exception as e:
            logger.error("Embedding generation failed", error=str(e))
            raise

    async def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.

        Args:
            query: Search query to embed

        Returns:
            Embedding vector optimized for search
        """
        try:
            result = self.client.embed(
                texts=[query],
                model=self.model,
                input_type="query"
            )

            embedding = result.embeddings[0]
            logger.info(
                "Query embedding generated",
                model=self.model,
                dimension=len(embedding),
            )
            return embedding

        except Exception as e:
            logger.error("Query embedding generation failed", error=str(e))
            raise

    async def embed_batch(
        self, texts: List[str], input_type: str = "document"
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            input_type: Type of input ("document" or "query")

        Returns:
            List of embedding vectors
        """
        try:
            result = self.client.embed(
                texts=texts,
                model=self.model,
                input_type=input_type
            )

            embeddings = result.embeddings
            logger.info(
                "Batch embeddings generated",
                model=self.model,
                count=len(embeddings),
            )
            return embeddings

        except Exception as e:
            logger.error("Batch embedding generation failed", error=str(e))
            raise


# Global client instance
voyage_client = VoyageClient()
