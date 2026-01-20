"""
Domain-based politeness system to avoid rate limiting
Tracks last request time per domain and adds delays
"""

import time
from typing import Dict, Optional
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class DomainPolitenessManager:
    """Manages request timing to be polite to domains"""
    
    def __init__(self, min_delay_between_requests: int = 30):
        """
        Initialize the politeness manager
        
        Args:
            min_delay_between_requests: Minimum seconds between requests to same domain
        """
        self.min_delay = min_delay_between_requests
        self.last_request_time: Dict[str, float] = {}
        self.domain_request_count: Dict[str, int] = {}
        
    def get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            return urlparse(url).netloc.lower()
        except:
            return "unknown"
    
    def should_wait(self, url: str) -> Optional[float]:
        """
        Check if we should wait before making a request
        
        Returns:
            Number of seconds to wait, or None if no wait needed
        """
        domain = self.get_domain(url)
        current_time = time.time()
        
        if domain not in self.last_request_time:
            return None
            
        time_since_last = current_time - self.last_request_time[domain]
        
        if time_since_last < self.min_delay:
            wait_time = self.min_delay - time_since_last
            logger.debug(f"Should wait {wait_time:.1f}s for domain {domain} (last request {time_since_last:.1f}s ago)")
            return wait_time
            
        return None
    
    def record_request(self, url: str):
        """Record that we made a request to this URL"""
        domain = self.get_domain(url)
        current_time = time.time()
        
        self.last_request_time[domain] = current_time
        self.domain_request_count[domain] = self.domain_request_count.get(domain, 0) + 1
        
        logger.debug(f"Recorded request to {domain} (total: {self.domain_request_count[domain]})")
    
    def get_stats(self) -> Dict[str, int]:
        """Get request statistics per domain"""
        return self.domain_request_count.copy()
    
    def reset_stats(self):
        """Reset all statistics"""
        self.last_request_time.clear()
        self.domain_request_count.clear()
