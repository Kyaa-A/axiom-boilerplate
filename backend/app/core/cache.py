"""
Redis cache client for caching and session storage.
"""
from typing import Any, Optional
import json

from redis.asyncio import Redis, ConnectionPool
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class CacheClient:
    """Async Redis cache client wrapper."""

    def __init__(self):
        self._pool: Optional[ConnectionPool] = None
        self._redis: Optional[Redis] = None

    async def connect(self) -> None:
        """Initialize Redis connection pool."""
        self._pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=True,
        )
        self._redis = Redis(connection_pool=self._pool)
        logger.info("Redis cache connected", url=settings.REDIS_URL)

    async def disconnect(self) -> None:
        """Close Redis connections."""
        if self._redis:
            await self._redis.close()
        if self._pool:
            await self._pool.disconnect()
        logger.info("Redis cache disconnected")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._redis:
            return None

        value = await self._redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(
        self, key: str, value: Any, expire: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            expire: Expiration time in seconds

        Returns:
            True if successful
        """
        if not self._redis:
            return False

        try:
            serialized = json.dumps(value) if not isinstance(value, str) else value
            await self._redis.set(key, serialized, ex=expire)
            return True
        except Exception as e:
            logger.error("Cache set error", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self._redis:
            return False

        result = await self._redis.delete(key)
        return bool(result)

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self._redis:
            return False

        result = await self._redis.exists(key)
        return bool(result)

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter in cache."""
        if not self._redis:
            return 0

        return await self._redis.incrby(key, amount)


# Global cache instance
cache_client = CacheClient()


async def get_cache() -> CacheClient:
    """Dependency for getting cache client."""
    return cache_client
