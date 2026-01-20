"""
Async domain politeness manager for non-blocking delays
"""

import asyncio
from typing import Dict, Optional
from urllib.parse import urlparse
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AsyncDomainPolitenessManager:
    """Manages request timing with async non-blocking delays"""
    
    def __init__(self, min_delay_between_requests: int = 5):
        """
        Initialize the async politeness manager
        
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
    
    async def wait_if_needed(self, url: str):
        """
        Wait asynchronously if we need to delay before making a request
        
        This is non-blocking - other async tasks can run during the wait
        """
        domain = self.get_domain(url)
        current_time = asyncio.get_event_loop().time()
        
        if domain not in self.last_request_time:
            return
            
        time_since_last = current_time - self.last_request_time[domain]
        
        if time_since_last < self.min_delay:
            wait_time = self.min_delay - time_since_last
            logger.info(f"Async politeness delay: waiting {wait_time:.1f}s for {domain}")
            await asyncio.sleep(wait_time)
            
    def record_request(self, url: str):
        """Record that we made a request to this URL"""
        domain = self.get_domain(url)
        current_time = asyncio.get_event_loop().time()
        
        self.last_request_time[domain] = current_time
        self.domain_request_count[domain] = self.domain_request_count.get(domain, 0) + 1
        
        logger.debug(f"Recorded request to {domain} (total: {self.domain_request_count[domain]})")
    
    def get_stats(self) -> Dict[str, int]:
        """Get request statistics per domain"""
        return self.domain_request_count.copy()
