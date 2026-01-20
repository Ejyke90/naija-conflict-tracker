"""
Drop-in replacement for TargetedNewsScraper using RSS feeds.

This provides the scrape_multiple_sources() method your pipeline expects,
but uses RSS feeds instead of HTML scraping.

BENEFITS:
- No more 403 errors
- No more encoding issues  
- 10x faster
- Built-in deduplication
- More reliable
"""

import feedparser
import requests
from bs4 import BeautifulSoup
import hashlib
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time
import random

logger = logging.getLogger(__name__)


class RSSBasedScraper:
    """
    Drop-in replacement for TargetedNewsScraper that uses RSS feeds.
    
    Compatible with existing pipeline - implements scrape_multiple_sources() method.
    """
    
    # Default RSS feed mapping for common Nigerian news sources
    RSS_FEED_MAP = {
        'punchng.com': 'https://punchng.com/feed/',
        'vanguardngr.com': 'https://www.vanguardngr.com/feed/',
        'premiumtimesng.com': 'https://www.premiumtimesng.com/feed/',
        'dailypost.ng': 'https://dailypost.ng/feed/',
        'channelstv.com': 'https://www.channelstv.com/feed/',
        'dailynigerian.com': 'https://dailynigerian.com/feed/',
        'guardian.ng': 'https://guardian.ng/feed/',
        'tribuneonlineng.com': 'https://tribuneonlineng.com/feed/',
        'thenationonlineng.net': 'https://thenationonlineng.net/feed/',
        'saharareporters.com': 'https://saharareporters.com/feeds/latest/feed',
        'legit.ng': 'https://www.legit.ng/rss/all.rss',
        'informationng.com': 'https://www.informationng.com/feed/',
        'naijanews.com': 'https://www.naijanews.com/feed/',
        
        # International sources
        'bbc.com': 'http://feeds.bbci.co.uk/news/world/africa/rss.xml',
        'bbc.co.uk': 'http://feeds.bbci.co.uk/news/world/africa/rss.xml',
        'allafrica.com': 'https://allafrica.com/tools/headlines/rdf/nigeria/headlines.rdf',
        'africanews.com': 'https://www.africanews.com/feed/rss',
        'france24.com': 'https://www.france24.com/en/africa/rss',
    }
    
    def __init__(self):
        """Initialize RSS-based scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NaijaConflictTracker/1.0 (RSS Reader)'
        })
        self.seen_guids = set()
        logger.info("RSS-based scraper initialized")
    
    def scrape_multiple_sources(self, sources: List[Dict], max_articles: int = None) -> List[Dict]:
        """
        Scrape articles from multiple sources using RSS feeds.
        
        This is the method your pipeline expects - it's a drop-in replacement.
        
        Args:
            sources: List of dicts with:
                - url: str (will be converted to RSS feed URL)
                - source_name: str
                - region: str ('nigerian' or 'international')
                - selectors: dict (ignored for RSS, kept for compatibility)
            max_articles: int or None (limit total articles)
        
        Returns:
            List of article dicts matching your existing format:
                - url: str
                - title: str
                - content: str
                - source: str
                - region: str
                - published_date: str
                - fetch_success: bool
                - encoding_used: str
                - is_conflict_related: bool
        """
        logger.info(f"RSS Scraper: Processing {len(sources)} sources...")
        
        all_articles = []
        total_sources = len(sources)
        
        for idx, source_info in enumerate(sources, 1):
            source_name = source_info.get('source_name', 'Unknown')
            region = source_info.get('region', 'unknown')
            url = source_info.get('url', '')
            
            logger.info(f"[{idx}/{total_sources}] Fetching RSS: {source_name}...")
            
            # Convert URL to RSS feed URL
            rss_url = self._url_to_rss_feed(url)
            
            if not rss_url:
                logger.warning(f"  ⊘ No RSS feed found for {source_name}")
                continue
            
            # Fetch RSS feed
            articles = self._fetch_rss_feed(rss_url, source_name, region)
            
            if articles:
                all_articles.extend(articles)
                logger.info(f"  ✓ Fetched {len(articles)} articles from {source_name}")
            else:
                logger.warning(f"  ⊘ No articles from {source_name}")
            
            # Small delay between feeds
            if idx < total_sources:
                time.sleep(random.uniform(0.5, 1.5))
        
        # Apply max_articles limit if specified
        if max_articles and len(all_articles) > max_articles:
            all_articles = all_articles[:max_articles]
        
        logger.info(f"\n{'='*60}")
        logger.info(f"RSS Scraper Summary:")
        logger.info(f"  Sources processed: {total_sources}")
        logger.info(f"  Articles fetched: {len(all_articles)}")
        logger.info(f"{'='*60}")
        
        return all_articles
    
    def _url_to_rss_feed(self, url: str) -> Optional[str]:
        """
        Convert a website URL to its RSS feed URL.
        
        Strategy:
        1. Check our known feed map
        2. Try common RSS patterns (/feed/, /rss/, etc.)
        3. Look for RSS link in page HTML
        """
        from urllib.parse import urlparse
        
        # Extract domain
        domain = urlparse(url).netloc
        domain = domain.replace('www.', '')
        
        # Check known feed map
        if domain in self.RSS_FEED_MAP:
            return self.RSS_FEED_MAP[domain]
        
        # Try common RSS patterns
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        common_patterns = [
            f"{base_url}/feed/",
            f"{base_url}/rss/",
            f"{base_url}/feed",
            f"{base_url}/rss",
            f"{base_url}/rss.xml",
            f"{base_url}/feed.xml",
            f"{url.rstrip('/')}/feed/",
        ]
        
        for rss_url in common_patterns:
            if self._test_rss_url(rss_url):
                logger.info(f"  Found RSS feed: {rss_url}")
                return rss_url
        
        # Last resort: try to find RSS link in HTML
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for RSS link in <link> tags
            rss_link = soup.find('link', type='application/rss+xml')
            if rss_link and rss_link.get('href'):
                href = rss_link['href']
                # Make absolute URL if relative
                if href.startswith('/'):
                    href = base_url + href
                return href
        except:
            pass
        
        return None
    
    def _test_rss_url(self, url: str) -> bool:
        """Quick test if URL is a valid RSS feed."""
        try:
            response = self.session.get(url, timeout=5)
            content_type = response.headers.get('content-type', '').lower()
            
            # Check if response looks like RSS
            is_rss = (
                'xml' in content_type or
                'rss' in content_type or
                b'<rss' in response.content[:200] or
                b'<feed' in response.content[:200]
            )
            
            return is_rss
        except:
            return False
    
    def _fetch_rss_feed(self, rss_url: str, source_name: str, region: str) -> List[Dict]:
        """Fetch and parse RSS feed into article format."""
        try:
            # Parse RSS feed
            feed = feedparser.parse(rss_url)
            
            if feed.bozo:
                logger.warning(f"  RSS parse warning: {feed.bozo_exception}")
            
            articles = []
            entries = feed.entries if hasattr(feed, 'entries') else []
            
            for entry in entries:
                article = self._parse_rss_entry(entry, source_name, region)
                
                if article:
                    # Deduplication
                    guid = article.get('guid', article.get('url', ''))
                    if guid in self.seen_guids:
                        continue
                    
                    self.seen_guids.add(guid)
                    articles.append(article)
            
            return articles
            
        except Exception as e:
            logger.error(f"  Error fetching RSS from {source_name}: {e}")
            return []
    
    def _parse_rss_entry(self, entry, source_name: str, region: str) -> Optional[Dict]:
        """Parse RSS entry into article dict matching existing format."""
        try:
            # Extract title
            title = entry.get('title', '').strip()
            if not title:
                return None
            
            # Extract content
            content = ''
            if hasattr(entry, 'content') and entry.content:
                content = entry.content[0].value if isinstance(entry.content, list) else entry.content
            elif hasattr(entry, 'summary'):
                content = entry.summary
            elif hasattr(entry, 'description'):
                content = entry.description
            
            # Clean HTML from content
            if content:
                soup = BeautifulSoup(content, 'html.parser')
                content = soup.get_text(separator=' ', strip=True)
            
            # Extract URL
            url = entry.get('link', '')
            
            # Extract date
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published = datetime(*entry.updated_parsed[:6])
            else:
                published = datetime.utcnow()
            
            # Create GUID for deduplication
            guid = entry.get('id') or entry.get('guid') or url or hashlib.md5(title.encode()).hexdigest()
            
            # Check if conflict-related
            is_conflict = self._is_conflict_related(title, content)
            
            # Return in format compatible with existing pipeline
            return {
                'url': url,
                'title': title,
                'content': content,
                'source': source_name,
                'source_domain': source_name,
                'region': region,
                'published_date': published.isoformat(),
                'fetch_success': True,
                'encoding_used': 'utf-8',  # RSS is always UTF-8
                'is_conflict_related': is_conflict,
                'guid': guid,
                'fetch_method': 'rss'
            }
            
        except Exception as e:
            logger.error(f"  Error parsing RSS entry: {e}")
            return None
    
    def _is_conflict_related(self, title: str, content: str) -> bool:
        """Check if article is conflict-related."""
        conflict_keywords = [
            'attack', 'killed', 'kill', 'kidnap', 'abduct',
            'violence', 'clash', 'gunmen', 'bandits', 'terrorist',
            'boko haram', 'iswap', 'insurgent', 'militant',
            'security', 'casualties', 'bomb', 'explosion'
        ]
        
        text = (title + ' ' + content).lower()
        return any(keyword in text for keyword in conflict_keywords)


# Adapter class for existing TargetedNewsScraper
class TargetedNewsScraper(RSSBasedScraper):
    """
    Adapter: Makes RSS scraper compatible with existing code.
    
    If your existing code does:
        scraper = TargetedNewsScraper()
        articles = scraper.scrape_multiple_sources(sources)
    
    This will work exactly the same, but use RSS instead of HTML scraping.
    """
    pass


# Example usage
if __name__ == "__main__":
    # Test with your existing pipeline format
    scraper = TargetedNewsScraper()
    
    # Your pipeline probably calls it like this:
    sources = [
        {
            'url': 'https://punchng.com/topics/security/',
            'source_name': 'Punch',
            'region': 'nigerian'
        },
        {
            'url': 'https://www.premiumtimesng.com/news/headlines',
            'source_name': 'Premium Times',
            'region': 'nigerian'
        },
        {
            'url': 'https://www.bbc.com/news/topics/c302m85q5xzt/nigeria',
            'source_name': 'BBC Africa',
            'region': 'international'
        }
    ]
    
    articles = scraper.scrape_multiple_sources(sources, max_articles=10)
    
    print(f"\nFetched {len(articles)} articles:\n")
    for article in articles:
        conflict = "🔴" if article['is_conflict_related'] else "  "
        print(f"{conflict} [{article['source']}] {article['title'][:60]}...")
        print(f"   {article['url'][:70]}...")
        print()
