import time
import logging
from typing import Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
import json
import asyncio
from app.core.cache import get_redis_client

logger = logging.getLogger(__name__)

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Simple performance monitoring middleware without external dependencies"""
    
    def __init__(self, app):
        super().__init__(app)
        self.request_times: Dict[str, list] = {}
        
    async def dispatch(self, request: Request, call_next):
        # Record start time
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate response time
        process_time = time.time() - start_time
        
        # Get endpoint path
        path = request.url.path
        method = request.method
        
        # Log performance data
        await self._log_performance_data(request, path, method, process_time, response.status_code)
        
        # Add performance headers
        response.headers["X-Process-Time"] = str(round(process_time, 4))
        
        return response
    
    async def _log_performance_data(self, request: Request, path: str, method: str, process_time: float, status_code: int):
        """Log and store performance data"""
        try:
            # Create performance record
            performance_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'path': path,
                'method': method,
                'response_time': process_time,
                'status_code': status_code
            }
            
            # Log to console
            logger.info(f"Performance: {method} {path} - {process_time:.4f}s - {status_code}")
            
            # Store in memory for recent metrics
            endpoint_key = f"{method}:{path}"
            if endpoint_key not in self.request_times:
                self.request_times[endpoint_key] = []
            
            self.request_times[endpoint_key].append({
                'timestamp': performance_data['timestamp'],
                'response_time': process_time,
                'status_code': status_code
            })
            
            # Keep only last 100 requests per endpoint
            if len(self.request_times[endpoint_key]) > 100:
                self.request_times[endpoint_key] = self.request_times[endpoint_key][-100:]
            
            # Get Redis client from app.state
            redis_client = None
            try:
                redis_client = request.app.state.redis_client
            except AttributeError:
                # Redis not available, will use memory-only storage
                pass
                
            # Store in Redis if available
            if redis_client:
                try:
                    redis_key = f"performance:{endpoint_key}"
                    await redis_client.lpush(redis_key, json.dumps(performance_data))
                    await redis_client.ltrim(redis_key, 0, 999)  # Keep last 1000 entries
                    await redis_client.expire(redis_key, 3600)  # Expire after 1 hour
                except Exception as e:
                    logger.warning(f"Failed to store performance data in Redis: {e}")
            
            # Alert on slow responses
            if process_time > 1.0:  # Alert if response time > 1 second
                logger.warning(f"Slow response detected: {method} {path} - {process_time:.4f}s")
                
        except Exception as e:
            logger.error(f"Error logging performance data: {e}")
    
    def get_endpoint_stats(self, endpoint_key: str) -> Dict[str, Any]:
        """Get performance statistics for a specific endpoint"""
        if endpoint_key not in self.request_times:
            return None
        
        requests = self.request_times[endpoint_key]
        if not requests:
            return None
        
        response_times = [req['response_time'] for req in requests]
        
        return {
            'endpoint': endpoint_key,
            'total_requests': len(requests),
            'avg_response_time': sum(response_times) / len(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'requests_per_second': len(requests) / 60.0,  # Assuming last minute of data
            'error_rate': sum(1 for req in requests if req['status_code'] >= 400) / len(requests),
            'last_request': requests[-1]['timestamp'] if requests else None
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get performance statistics for all endpoints"""
        stats = {}
        for endpoint_key in self.request_times:
            stats[endpoint_key] = self.get_endpoint_stats(endpoint_key)
        return stats
    
    def get_slow_endpoints(self, threshold: float = 0.5) -> list:
        """Get endpoints with average response time above threshold"""
        slow_endpoints = []
        for endpoint_key in self.request_times:
            endpoint_stats = self.get_endpoint_stats(endpoint_key)
            if endpoint_stats and endpoint_stats['avg_response_time'] > threshold:
                slow_endpoints.append(endpoint_stats)
        
        return sorted(slow_endpoints, key=lambda x: x['avg_response_time'], reverse=True)
