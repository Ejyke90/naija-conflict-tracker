"""
Hybrid caching strategy for dashboard data access
Implements multi-layer caching: Redis cache + query paging + connection pooling
"""
import json
import logging
from typing import Any, Callable, List, Optional, Dict, Tuple
from datetime import datetime, timedelta
import asyncio

from app.core.cache import get_redis_client

logger = logging.getLogger(__name__)


class HybridCachingStrategy:
    """
    Multi-layer caching strategy for dashboard performance
    
    Layers:
    1. Redis Cache (TTL-based) - Fast, distributed, with graceful stale-data fallback
    2. Query Pagination - For state comparisons with >10 states
    3. Connection Pooling - Handled at database layer (SQLAlchemy)
    """
    
    def __init__(self):
        self.redis = None
    
    async def get_redis_client(self):
        """Lazy-initialize Redis client"""
        if self.redis is None:
            self.redis = await get_redis_client()
        return self.redis
    
    async def get_or_fetch(
        self,
        cache_key: str,
        fetch_func: Callable,
        ttl_seconds: int = 1800,
        allow_stale: bool = True,
        max_stale_age_hours: int = 24
    ) -> Tuple[Any, bool, Optional[datetime]]:
        """
        Get data from cache or fetch from source.
        
        Returns:
            Tuple of (data, is_from_cache, cache_timestamp)
        """
        cache = await self.get_redis_client()
        
        # Try to get fresh data from cache
        if cache:
            try:
                cached_data = await cache.get(cache_key)
                if cached_data:
                    data = json.loads(cached_data)
                    logger.debug(f"Cache hit: {cache_key}")
                    return data["value"], True, data.get("cached_at")
            except Exception as e:
                logger.warning(f"Redis cache miss for {cache_key}: {str(e)}")
        
        # Fetch fresh data from source
        try:
            logger.debug(f"Cache miss, fetching: {cache_key}")
            data = await fetch_func()
            
            # Cache the result
            if cache and data:
                try:
                    cache_value = {
                        "value": data,
                        "cached_at": datetime.utcnow().isoformat(),
                        "ttl": ttl_seconds
                    }
                    await cache.set(
                        cache_key,
                        json.dumps(cache_value),
                        ex=ttl_seconds
                    )
                except Exception as e:
                    logger.warning(f"Failed to cache {cache_key}: {str(e)}")
            
            return data, False, None
        
        except Exception as e:
            logger.error(f"Error fetching {cache_key}: {str(e)}")
            
            # Try to serve stale data if allowed
            if allow_stale and cache:
                try:
                    # Set a longer TTL to preserve stale data
                    # Look for stale data by checking all potential cache keys
                    cached_data = await cache.get(f"{cache_key}:stale")
                    if cached_data:
                        data = json.loads(cached_data)
                        cached_at = datetime.fromisoformat(data.get("cached_at", datetime.utcnow().isoformat()))
                        age_hours = (datetime.utcnow() - cached_at).total_seconds() / 3600
                        
                        if age_hours <= max_stale_age_hours:
                            logger.warning(f"Serving stale cache ({age_hours:.1f}h old) for {cache_key}")
                            return data["value"], True, cached_at
                except Exception as stale_error:
                    logger.warning(f"Failed to retrieve stale cache: {str(stale_error)}")
            
            raise
    
    async def serve_stale(
        self,
        cache_key: str,
        max_age_hours: int = 24
    ) -> Optional[Tuple[Any, datetime]]:
        """
        Serve stale cached data if database is unavailable.
        
        Returns:
            Tuple of (data, cached_at) if available, None otherwise
        """
        cache = await self.get_redis_client()
        
        if not cache:
            return None
        
        try:
            # Try to get any cached version (even expired)
            cached_data = await cache.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                cached_at = datetime.fromisoformat(
                    data.get("cached_at", datetime.utcnow().isoformat())
                )
                age_hours = (datetime.utcnow() - cached_at).total_seconds() / 3600
                
                if age_hours <= max_age_hours:
                    logger.info(f"Serving stale cache ({age_hours:.1f}h old) for {cache_key}")
                    return data["value"], cached_at
        except Exception as e:
            logger.warning(f"Error retrieving stale cache for {cache_key}: {str(e)}")
        
        return None
    
    @staticmethod
    def batch_pagination(
        items: List[Any],
        page_size: int = 10
    ) -> Tuple[List[Any], int, int]:
        """
        Paginate a list of items for efficient processing.
        
        Useful for state comparisons with >10 states to fetch top states first,
        defer loading remaining states.
        
        Returns:
            Tuple of (first_page_items, total_items, pages_remaining)
        """
        total = len(items)
        first_page = items[:page_size]
        remaining = total - page_size
        
        return first_page, total, max(0, remaining)
    
    @staticmethod
    def add_cache_metadata(
        response: Dict[str, Any],
        is_cached: bool,
        cached_at: Optional[datetime] = None,
        status: str = "ok"
    ) -> Dict[str, Any]:
        """
        Add cache metadata to API response.
        
        Args:
            response: Original response dict
            is_cached: Whether response came from cache
            cached_at: When data was cached
            status: Response status (ok, degraded, error)
        
        Returns:
            Response with added metadata fields
        """
        response["status"] = status
        response["cached"] = is_cached
        
        if cached_at:
            response["cached_at"] = cached_at.isoformat()
        else:
            response["cached_at"] = None
        
        return response
