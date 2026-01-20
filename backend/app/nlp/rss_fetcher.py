"""
RSS-Based News Fetcher for Naija Conflict Tracker

Benefits over web scraping:
- No 403 errors (RSS feeds are public APIs)
- No encoding issues (RSS is standardized XML/UTF-8)
- Faster (just parse XML, no HTML scraping)
- Built-in deduplication (GUID fields)
- Timestamps included
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
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RSSNewsFetcher:
    """
    Fetch news articles from RSS feeds instead of scraping HTML.
    Much more reliable and faster than traditional web scraping.
    """
    
    def __init__(self, config_path: str = "rss_feeds_config.json"):
        """
        Initialize RSS fetcher.
        
        Args:
            config_path: Path to RSS feeds configuration file
        """
        self.config = self._load_config(config_path)
        self.seen_guids = set()  # Track articles we've already processed
        self.session = requests.Session()
        
        # Minimal headers (RSS feeds don't need fancy browser headers)
        self.session.headers.update({
            'User-Agent': 'NaijaConflictTracker/1.0 (RSS Reader)',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*'
        })
        
        logger.info("RSS Fetcher initialized")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load RSS feeds configuration."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config not found: {config_path}, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Default configuration with essential feeds."""
        return {
            "feeds": [
                # Tier 1 - Must have
                {"name": "Punch Nigeria", "url": "https://punchng.com/feed/", "region": "nigerian", "priority": 1},
                {"name": "Premium Times", "url": "https://www.premiumtimesng.com/feed/", "region": "nigerian", "priority": 1},
                {"name": "BBC Africa", "url": "http://feeds.bbci.co.uk/news/world/africa/rss.xml", "region": "international", "priority": 1},
                {"name": "AllAfrica Nigeria", "url": "https://allafrica.com/tools/headlines/rdf/nigeria/headlines.rdf", "region": "nigerian", "priority": 1},
                {"name": "Africanews", "url": "https://www.africanews.com/feed/rss", "region": "international", "priority": 1},
                
                # Tier 2 - Important
                {"name": "Vanguard", "url": "https://www.vanguardngr.com/feed/", "region": "nigerian", "priority": 2},
                {"name": "AllAfrica Conflict", "url": "https://allafrica.com/tools/headlines/rdf/conflict/headlines.rdf", "region": "specialized", "priority": 2},
                {"name": "Channels TV", "url": "https://www.channelstv.com/feed/", "region": "nigerian", "priority": 2},
                {"name": "Daily Post", "url": "https://dailypost.ng/feed/", "region": "nigerian", "priority": 2},
                {"name": "France 24 Africa", "url": "https://www.france24.com/en/africa/rss", "region": "international", "priority": 2},
            ],
            "settings": {
                "max_age_hours": 48,  # Only fetch articles from last 48 hours
                "require_nigeria_keywords": ["international", "specialized"],  # Regions that need filtering
                "nigeria_keywords": ["nigeria", "nigerian", "lagos", "abuja", "boko haram", "iswap", "kano", "kaduna"],
                "conflict_keywords": ["attack", "killed", "kidnap", "abduct", "violence", "clash", "gunmen", "bandits"]
            }
        }
    
    def fetch_feed(self, feed_config: Dict) -> List[Dict]:
        """
        Fetch and parse a single RSS feed.
        
        Args:
            feed_config: Dict with 'name', 'url', 'region', 'priority'
            
        Returns:
            List of article dicts
        """
        feed_url = feed_config['url']
        feed_name = feed_config['name']
        region = feed_config.get('region', 'unknown')
        
        try:
            logger.info(f"Fetching RSS feed: {feed_name}...")
            
            # Parse RSS feed
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:  # feedparser sets bozo=1 if there's an error
                logger.warning(f"Feed parse warning for {feed_name}: {feed.bozo_exception}")
            
            articles = []
            entries = feed.entries if hasattr(feed, 'entries') else []
            
            logger.info(f"  Found {len(entries)} entries in feed")
            
            for entry in entries:
                article = self._parse_entry(entry, feed_config)
                
                if article:
                    # Check if we've seen this article before
                    if article['guid'] in self.seen_guids:
                        logger.debug(f"  ⊘ Skipping duplicate: {article['title'][:50]}...")
                        continue
                    
                    # Filter by age
                    if not self._is_recent(article):
                        logger.debug(f"  ⊘ Skipping old article: {article['title'][:50]}...")
                        continue
                    
                    # Filter international sources for Nigeria relevance
                    if region in self.config.get('settings', {}).get('require_nigeria_keywords', []):
                        if not self._is_nigeria_related(article):
                            logger.debug(f"  ⊘ Filtered (not Nigeria): {article['title'][:50]}...")
                            continue
                    
                    articles.append(article)
                    self.seen_guids.add(article['guid'])
                    logger.info(f"  ✓ {article['title'][:60]}...")
            
            logger.info(f"  Accepted {len(articles)}/{len(entries)} articles from {feed_name}")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching {feed_name}: {e}")
            return []
    
    def _parse_entry(self, entry, feed_config: Dict) -> Optional[Dict]:
        """Parse a single RSS entry into article dict."""
        try:
            # Extract title
            title = entry.get('title', '').strip()
            if not title:
                return None
            
            # Extract content (RSS feeds have different content fields)
            content = ''
            
            # Try different content fields in order of preference
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
            
            # Extract link
            link = entry.get('link', '')
            
            # Extract published date
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published = datetime(*entry.updated_parsed[:6])
            else:
                published = datetime.utcnow()  # Fallback to now
            
            # Create unique GUID for deduplication
            guid = entry.get('id') or entry.get('guid') or link or hashlib.md5(title.encode()).hexdigest()
            
            # Extract author if available
            author = entry.get('author', '')
            
            # Extract categories/tags
            categories = []
            if hasattr(entry, 'tags'):
                categories = [tag.term for tag in entry.tags]
            
            return {
                'title': title,
                'content': content,
                'url': link,
                'published_date': published.isoformat() if isinstance(published, datetime) else str(published),
                'published_datetime': published,
                'guid': guid,
                'source': feed_config['name'],
                'region': feed_config.get('region', 'unknown'),
                'priority': feed_config.get('priority', 3),
                'author': author,
                'categories': categories,
                'fetch_success': True,
                'fetch_method': 'rss'
            }
            
        except Exception as e:
            logger.error(f"Error parsing entry: {e}")
            return None
    
    def _is_recent(self, article: Dict) -> bool:
        """Check if article is within max age threshold."""
        max_age_hours = self.config.get('settings', {}).get('max_age_hours', 48)
        
        published = article.get('published_datetime')
        if not isinstance(published, datetime):
            return True  # If we can't parse date, include it
        
        age = datetime.utcnow() - published
        return age <= timedelta(hours=max_age_hours)
    
    def _is_nigeria_related(self, article: Dict) -> bool:
        """Check if article is related to Nigeria (for international sources)."""
        keywords = self.config.get('settings', {}).get('nigeria_keywords', [])
        
        text = (article.get('title', '') + ' ' + article.get('content', '')).lower()
        
        return any(keyword.lower() in text for keyword in keywords)
    
    def _is_conflict_related(self, article: Dict) -> bool:
        """Check if article is related to conflict/security."""
        keywords = self.config.get('settings', {}).get('conflict_keywords', [])
        
        text = (article.get('title', '') + ' ' + article.get('content', '')).lower()
        
        has_conflict = any(keyword.lower() in text for keyword in keywords)
        article['is_conflict_related'] = has_conflict
        
        return has_conflict
    
    def fetch_all_feeds(self, 
                       max_priority: int = None,
                       regions: List[str] = None,
                       delay_between: float = 1.0) -> List[Dict]:
        """
        Fetch articles from all configured RSS feeds.
        
        Args:
            max_priority: Only fetch feeds with priority <= this (1=highest priority)
            regions: List of regions to include ['nigerian', 'international', 'specialized']
            delay_between: Seconds to wait between feed fetches
            
        Returns:
            List of all articles from all feeds
        """
        feeds = self.config.get('feeds', [])
        
        # Filter by priority
        if max_priority is not None:
            feeds = [f for f in feeds if f.get('priority', 999) <= max_priority]
        
        # Filter by region
        if regions:
            feeds = [f for f in feeds if f.get('region') in regions]
        
        logger.info(f"Fetching {len(feeds)} RSS feeds...")
        
        all_articles = []
        stats = {
            'feeds_attempted': 0,
            'feeds_successful': 0,
            'total_entries': 0,
            'accepted_articles': 0,
            'by_region': {}
        }
        
        for idx, feed_config in enumerate(feeds, 1):
            stats['feeds_attempted'] += 1
            region = feed_config.get('region', 'unknown')
            
            if region not in stats['by_region']:
                stats['by_region'][region] = {'attempted': 0, 'articles': 0}
            
            stats['by_region'][region]['attempted'] += 1
            
            # Fetch feed
            articles = self.fetch_feed(feed_config)
            
            if articles:
                stats['feeds_successful'] += 1
                stats['total_entries'] += len(articles)
                stats['accepted_articles'] += len(articles)
                stats['by_region'][region]['articles'] += len(articles)
                
                # Tag conflict-related articles
                for article in articles:
                    self._is_conflict_related(article)
                
                all_articles.extend(articles)
            
            # Delay between feeds (be polite)
            if idx < len(feeds):
                time.sleep(delay_between)
        
        # Sort by priority and date
        all_articles.sort(key=lambda x: (x.get('priority', 999), x.get('published_datetime', datetime.min)), reverse=True)
        
        # Log summary
        logger.info(f"\n{'='*60}")
        logger.info(f"RSS Fetch Summary:")
        logger.info(f"  Feeds: {stats['feeds_successful']}/{stats['feeds_attempted']} successful")
        logger.info(f"  Articles: {stats['accepted_articles']} total")
        for region, data in stats['by_region'].items():
            logger.info(f"    • {region}: {data['articles']} articles")
        
        conflict_count = sum(1 for a in all_articles if a.get('is_conflict_related'))
        logger.info(f"  Conflict-related: {conflict_count}/{len(all_articles)}")
        logger.info(f"{'='*60}")
        
        return all_articles
    
    def save_seen_guids(self, filepath: str = "seen_articles.json"):
        """Save GUIDs of seen articles to avoid reprocessing."""
        try:
            with open(filepath, 'w') as f:
                json.dump(list(self.seen_guids), f)
            logger.info(f"Saved {len(self.seen_guids)} seen article GUIDs")
        except Exception as e:
            logger.error(f"Error saving seen GUIDs: {e}")
    
    def load_seen_guids(self, filepath: str = "seen_articles.json"):
        """Load previously seen article GUIDs."""
        try:
            if Path(filepath).exists():
                with open(filepath, 'r') as f:
                    self.seen_guids = set(json.load(f))
                logger.info(f"Loaded {len(self.seen_guids)} previously seen article GUIDs")
        except Exception as e:
            logger.error(f"Error loading seen GUIDs: {e}")


# Example usage and testing
if __name__ == "__main__":
    # Initialize fetcher
    fetcher = RSSNewsFetcher()
    
    # Load previously seen articles (avoid duplicates)
    fetcher.load_seen_guids()
    
    # Fetch from all feeds
    # Option 1: All feeds
    articles = fetcher.fetch_all_feeds()
    
    # Option 2: Only Tier 1 feeds (fastest)
    # articles = fetcher.fetch_all_feeds(max_priority=1)
    
    # Option 3: Only Nigerian sources
    # articles = fetcher.fetch_all_feeds(regions=['nigerian'])
    
    # Option 4: Nigerian + Conflict-focused feeds
    # articles = fetcher.fetch_all_feeds(regions=['nigerian', 'specialized'])
    
    # Save seen GUIDs for next run
    fetcher.save_seen_guids()
    
    # Display results
    print(f"\n{'='*60}")
    print(f"FETCHED {len(articles)} ARTICLES")
    print(f"{'='*60}\n")
    
    # Show by source
    by_source = {}
    for article in articles:
        source = article['source']
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(article)
    
    for source, arts in by_source.items():
        print(f"\n{source} ({len(arts)} articles):")
        for a in arts[:3]:  # Show first 3
            conflict_tag = "🔴" if a.get('is_conflict_related') else "  "
            print(f"  {conflict_tag} {a['title'][:70]}...")
            print(f"     {a['published_date'][:10]} | {a['url'][:60]}...")
    
    # Show conflict articles
    conflict_articles = [a for a in articles if a.get('is_conflict_related')]
    print(f"\n{'='*60}")
    print(f"CONFLICT-RELATED ARTICLES: {len(conflict_articles)}")
    print(f"{'='*60}")
    for a in conflict_articles[:10]:
        print(f"  🔴 {a['source']}: {a['title'][:60]}...")
