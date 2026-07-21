"""Redis client configuration and utilities."""

from redis.asyncio import Redis, from_url

from app.config import get_settings

settings = get_settings()

redis_client: Redis = from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
    max_connections=50,
)


async def get_redis() -> Redis:
    """Dependency that provides a Redis client.

    Returns:
        Redis: Async Redis client instance.
    """
    return redis_client


async def cache_get(key: str) -> str | None:
    """Get a value from Redis cache.

    Args:
        key: Cache key.

    Returns:
        Cached value or None if not found.
    """
    return await redis_client.get(key)


async def cache_set(key: str, value: str, ttl: int = 3600) -> None:
    """Set a value in Redis cache with TTL.

    Args:
        key: Cache key.
        value: Value to cache.
        ttl: Time-to-live in seconds (default: 1 hour).
    """
    await redis_client.set(key, value, ex=ttl)


async def cache_delete(key: str) -> None:
    """Delete a value from Redis cache.

    Args:
        key: Cache key to delete.
    """
    await redis_client.delete(key)
