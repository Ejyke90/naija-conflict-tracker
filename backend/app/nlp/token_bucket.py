"""
Token bucket rate limiter - no blocking delays!
"""

import time
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class TokenBucket:
    """Token bucket for rate limiting without blocking"""
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket
        
        Args:
            capacity: Maximum tokens in bucket
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        
    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens without blocking
        
        Returns:
            True if tokens were consumed, False if not enough tokens
        """
        # Refill tokens based on time passed
        now = time.time()
        time_passed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + time_passed * self.refill_rate)
        self.last_refill = now
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def wait_time(self, tokens: int = 1) -> Optional[float]:
        """
        Calculate how long to wait for tokens (without actually waiting)
        
        Returns:
            Seconds to wait, or None if tokens are available
        """
        if self.consume(tokens):
            return None
        
        # Calculate time needed for refill
        needed = tokens - self.tokens
        return needed / self.refill_rate

class GroqRateLimiter:
    """Rate limiter specifically for Groq API"""
    
    def __init__(self):
        # Groq free tier: ~30 requests per minute sustained
        # Start with conservative limits
        self.bucket = TokenBucket(capacity=5, refill_rate=0.1)  # 1 request per 10 seconds
        
    def can_proceed(self) -> bool:
        """Check if we can make a request now"""
        return self.bucket.consume()
    
    def get_wait_time(self) -> Optional[float]:
        """Get how long to wait without blocking"""
        return self.bucket.wait_time()
    
    def record_request(self):
        """Record a successful request (already done by consume)"""
        pass
