"""
Redis Caching for Forecast Endpoints
Improves response times and reduces computational load
"""

from functools import wraps
import redis.asyncio as redis
import json
import logging
from typing import Optional, Callable, Any
from datetime import timedelta
from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis client (singleton)
redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Get or create Redis client"""
    global redis_client
    
    if redis_client is None:
        try:
            redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5
            )
            await redis_client.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            redis_client = None
    
    return redis_client


def cache_forecast(
    ttl: int = 3600,  # 1 hour default
    key_prefix: str = "forecast"
):
    """
    Decorator to cache forecast results in Redis
    
    Args:
        ttl: Time-to-live in seconds (default 1 hour)
        key_prefix: Redis key prefix
        
    Usage:
        @cache_forecast(ttl=7200, key_prefix="prophet_forecast")
        async def my_forecast_endpoint(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Build cache key from function arguments
            cache_key = f"{key_prefix}:{func.__name__}:{_build_cache_key(**kwargs)}"
            
            # Try to get from cache
            client = await get_redis_client()
            
            if client is not None:
                try:
                    cached = await client.get(cache_key)
                    if cached:
                        logger.info(f"Cache hit: {cache_key}")
                        return json.loads(cached)
                except Exception as e:
                    logger.warning(f"Cache read error: {e}")
            
            # Cache miss - compute result
            logger.info(f"Cache miss: {cache_key}")
            result = await func(*args, **kwargs)
            
            # Store in cache
            if client is not None and result:
                try:
                    await client.setex(
                        cache_key,
                        ttl,
                        json.dumps(result, default=str)
                    )
                    logger.info(f"Cached result: {cache_key} (TTL: {ttl}s)")
                except Exception as e:
                    logger.warning(f"Cache write error: {e}")
            
            return result
        
        return wrapper
    return decorator


def _build_cache_key(**kwargs) -> str:
    """Build consistent cache key from kwargs"""
    # Sort keys for consistency
    key_parts = [f"{k}={v}" for k, v in sorted(kwargs.items()) if v is not None]
    return ":".join(key_parts)


async def invalidate_forecast_cache(
    location: Optional[str] = None,
    pattern: Optional[str] = None
):
    """
    Invalidate cached forecasts
    
    Args:
        location: Invalidate for specific location
        pattern: Redis key pattern (e.g., "forecast:*:Borno")
    """
    client = await get_redis_client()
    
    if client is None:
        return
    
    try:
        if pattern:
            keys = await client.keys(pattern)
        elif location:
            keys = await client.keys(f"forecast:*:{location}*")
        else:
            keys = await client.keys("forecast:*")
        
        if keys:
            await client.delete(*keys)
            logger.info(f"Invalidated {len(keys)} cache keys")
    except Exception as e:
        logger.error(f"Cache invalidation error: {e}")


async def get_cache_stats() -> dict:
    """Get Redis cache statistics"""
    client = await get_redis_client()
    
    if client is None:
        return {"status": "disabled"}
    
    try:
        info = await client.info("stats")
        keys_count = await client.dbsize()
        
        return {
            "status": "connected",
            "keys": keys_count,
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
            "hit_rate": round(
                info.get("keyspace_hits", 0) / 
                max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1) * 100, 
                2
            )
        }
    except Exception as e:
        logger.error(f"Cache stats error: {e}")
        return {"status": "error", "message": str(e)}
