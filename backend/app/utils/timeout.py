"""
Timeout decorator for async functions with fallback support
"""
import asyncio
import functools
import logging
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


def with_timeout(seconds: int = 15, fallback_response: Optional[Dict[str, Any]] = None):
    """
    Decorator to add timeout protection to async functions.
    
    If query takes longer than specified seconds, returns fallback response
    with status='degraded' to indicate timeout.
    
    Args:
        seconds: Timeout duration in seconds (default: 15)
        fallback_response: Response to return on timeout (default: graceful empty response)
    
    Usage:
        @with_timeout(seconds=15)
        async def get_monthly_trends(state: str):
            # If this takes >15 seconds, returns {"status": "degraded", "data": [], ...}
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                # Execute function with timeout
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=seconds
                )
                return result
            except asyncio.TimeoutError:
                logger.warning(f"Function {func.__name__} exceeded {seconds}s timeout")
                
                # Return graceful degraded response
                if fallback_response:
                    return fallback_response
                
                # Default timeout response
                return {
                    "status": "degraded",
                    "data": [],
                    "message": f"Request exceeded {seconds}s timeout; serving cached data if available",
                    "cached": True,
                    "timeout": True
                }
        
        return wrapper
    return decorator
