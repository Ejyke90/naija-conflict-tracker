"""
Redis Caching for Forecast Endpoints
Improves response times and reduces computational load
"""

from functools import wraps
import redis.asyncio as redis
import json
import logging
import asyncio
from typing import Optional, Callable, Any
from datetime import timedelta
from app.core.config import settings
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

# Cache TTL configurations (in seconds)
CACHE_TTL = {
    "forecasts": 3600,        # 1 hour - predictions change slowly
    "timeseries": 1800,       # 30 minutes - historical data updates periodically
    "intelligence": 3600,     # 1 hour - archetypes/triggers relatively stable
    "hotspots": 1800,         # 30 minutes - hotspots change frequently
    "risk_scores": 3600,      # 1 hour - risk calculations
    "states": 86400,          # 24 hours - reference data rarely changes
    "state_overview": 300,    # 5 minutes - state detail page aggregations
    "state_rankings": 1800,   # 30 minutes - ranking table data
}

# Circuit breaker state
circuit_breaker_state = {
    "failures": 0,
    "last_failure": None,
    "is_open": False,
    "reset_time": 60  # seconds
}

# Redis client (singleton)
redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Get or create Railway-optimized Redis client with circuit breaker"""
    global redis_client, circuit_breaker_state

    # Check circuit breaker
    if circuit_breaker_state["is_open"]:
        if (asyncio.get_event_loop().time() - circuit_breaker_state["last_failure"] > 
            circuit_breaker_state["reset_time"]):
            circuit_breaker_state["is_open"] = False
            circuit_breaker_state["failures"] = 0
            logger.info("Circuit breaker reset")
        else:
            return None

    if redis_client is None:
        try:
            # Railway-optimized Redis client configuration
            redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                # Railway-specific optimizations - flattened for new redis-py versions
                max_connections=20,          # Prevent connection pool exhaustion
                socket_connect_timeout=1.0,  # Fast fail for Railway health checks
                socket_keepalive=True,       # Keep connections alive
                socket_keepalive_options={},
                retry_on_timeout=False,      # Don't retry - fail fast for HA
                health_check_interval=30,    # Check connection health
            )
            # Test connection with short timeout
            await asyncio.wait_for(redis_client.ping(), timeout=1.0)
            logger.info("Redis connected successfully (Railway optimized)")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            redis_client = None
            _record_circuit_breaker_failure()

    return redis_client


def _record_circuit_breaker_failure():
    """Record a circuit breaker failure"""
    global circuit_breaker_state
    circuit_breaker_state["failures"] += 1
    circuit_breaker_state["last_failure"] = asyncio.get_event_loop().time()
    
    if circuit_breaker_state["failures"] >= 3:
        circuit_breaker_state["is_open"] = True
        logger.warning("Circuit breaker opened due to repeated failures")


async def get_from_cache_resilient(cache_key: str):
    """Get data from cache with fail-soft pattern (Railway optimized)"""
    try:
        client = await get_redis_client()
        if client is None:
            return None
        
        # Railway-optimized timeout - longer for internal network
        cached = await asyncio.wait_for(client.get(cache_key), timeout=1.0)
        return cached
    except (RedisError, asyncio.TimeoutError) as e:
        logger.warning(f"Redis Cache Unavailable for {cache_key}: {e}")
        _record_circuit_breaker_failure()
        return None


async def set_cache_resilient(cache_key: str, data: Any, ttl: int = 3600):
    """Set cache data with fail-soft pattern (Railway optimized)"""
    try:
        client = await get_redis_client()
        if client is None:
            return
        
        # Fire and forget with reasonable timeout for Railway
        asyncio.create_task(
            asyncio.wait_for(
                client.setex(cache_key, ttl, json.dumps(data, default=str)),
                timeout=2.0  # Longer timeout for Railway internal network
            )
        )
    except (RedisError, asyncio.TimeoutError) as e:
        logger.warning(f"Redis Cache Write Failed for {cache_key}: {e}")
        _record_circuit_breaker_failure()


def cache_forecast(
    ttl: int = 3600,  # 1 hour default
    key_prefix: str = "forecast"
):
    """
    Decorator to cache forecast results in Redis with fail-soft pattern
    
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
            
            # Try to get from cache (resilient)
            cached = await get_from_cache_resilient(cache_key)
            if cached:
                logger.info(f"Cache hit: {cache_key}")
                return json.loads(cached)
            
            # Cache miss - compute result
            logger.info(f"Cache miss: {cache_key}")
            result = await func(*args, **kwargs)
            
            # Store in cache (fire and forget)
            if result:
                await set_cache_resilient(cache_key, result, ttl)
                logger.info(f"Caching result: {cache_key} (TTL: {ttl}s)")
            
            return result
        
        return wrapper
    return decorator


def _build_cache_key(**kwargs) -> str:
    """Build consistent cache key from kwargs"""
    # Sort keys for consistency
    key_parts = [f"{k}={v}" for k, v in sorted(kwargs.items()) if v is not None]
    return ":".join(key_parts)


def cache_key(*args) -> str:
    """Helper to build cache keys from arguments"""
    return ":".join(str(arg) for arg in args if arg is not None)


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
