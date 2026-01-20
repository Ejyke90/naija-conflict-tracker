"""
Targeted News Scraper for NLP Event Extraction
Focuses on high-quality Nigerian news outlets for conflict event extraction
"""

import requests
import feedparser
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import time
import hashlib
from urllib.parse import urljoin, urlparse
import re

logger = logging.getLogger(__name__)

class TargetedNewsScraper:
    """Scraper for targeted Nigerian news outlets optimized for NLP extraction"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1'
        })
        
        # Targeted Nigerian news sources with high-quality conflict reporting
        self.target_sources = {
            'punch': {
                'name': 'Punch Newspapers',
                'rss_url': 'https://punchng.com/feed/',
                'base_url': 'https://punchng.com',
                'regions': ['national', 'metro', 'south-west', 'south-south', 'south-east', 'north'],
                'quality_score': 0.9,
                'conflict_focus': True
            },
            'channels_tv': {
                'name': 'Channels Television',
                'rss_url': 'https://www.channelstv.com/feed/',
                'base_url': 'https://www.channelstv.com',
                'regions': ['national', 'politics', 'metro', 'north', 'south-south'],
                'quality_score': 0.95,
                'conflict_focus': True
            },
            'daily_nigerian': {
                'name': 'Daily Nigerian',
                'rss_url': 'https://dailynigerian.com/feed/',
                'base_url': 'https://dailynigerian.com',
                'regions': ['national', 'security', 'north', 'south-south'],
                'quality_score': 0.85,
                'conflict_focus': True
            },
            'vanguard': {
                'name': 'Vanguard News',
                'rss_url': 'https://www.vanguardngr.com/feed/',
                'base_url': 'https://www.vanguardngr.com',
                'regions': ['national', 'politics', 'metro', 'south-south', 'south-east', 'north'],
                'quality_score': 0.88,
                'conflict_focus': True
            },
            'daily_trust': {
                'name': 'Daily Trust',
                'rss_url': 'https://www.dailytrust.com.ng/feed/',
                'base_url': 'https://www.dailytrust.com.ng',
                'regions': ['national', 'north', 'north-west', 'north-east'],
                'quality_score': 0.92,
                'conflict_focus': True
            }
        }
        
        # Conflict-related keywords for filtering
        self.conflict_keywords = [
            'conflict', 'violence', 'attack', 'killed', 'dead', 'fatalities', 'casualties',
            'kidnapping', 'abduction', 'bandit', 'terrorist', 'boko haram', 'ipob', 'unknown gunmen',
            'clash', 'communal', 'ethnic', 'religious', 'herders', 'farmers', 'cattle rustling',
            'militant', 'insurgency', 'security', 'military', 'police', 'army', 'shooting',
            'bomb', 'explosion', 'armed', 'gunmen', 'robbery', 'raid', 'invasion',
            'displacement', 'refugees', 'crisis', 'unrest', 'protest', 'riot', 'curfew'
        ]
        
        # Location keywords for Nigerian states
        self.nigerian_states = [
            'abia', 'adamawa', 'akwa ibom', 'anambra', 'bauchi', 'bayelsa', 'benue', 'borno',
            'cross river', 'delta', 'ebonyi', 'edo', 'ekiti', 'enugu', 'gombe', 'imo',
            'jigawa', 'kaduna', 'kano', 'katsina', 'kebbi', 'kogi', 'kwara', 'lagos',
            'nasarawa', 'niger', 'ogun', 'ondo', 'osun', 'oyo', 'plateau', 'rivers',
            'sokoto', 'taraba', 'yobe', 'zamfara', 'fct', 'abuja'
        ]

    def scrape_recent_articles(self, hours_back: int = 6) -> List[Dict[str, Any]]:
        """
        Scrape recent articles from all targeted sources
        
        Args:
            hours_back: Number of hours to look back for articles
            
        Returns:
            List of articles ready for NLP extraction
        """
        all_articles = []
        
        for source_key, source_config in self.target_sources.items():
            try:
                logger.info(f"Scraping {source_config['name']}...")
                articles = self._scrape_source(source_key, source_config, hours_back)
                
                # Filter for conflict-related articles
                conflict_articles = self._filter_conflict_articles(articles)
                
                # Add source metadata
                for article in conflict_articles:
                    article['source_key'] = source_key
                    article['source_quality'] = source_config['quality_score']
                    article['scraped_at'] = datetime.utcnow().isoformat()
                
                all_articles.extend(conflict_articles)
                logger.info(f"Found {len(conflict_articles)} conflict articles from {source_config['name']}")
                
                # Respect rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error scraping {source_key}: {str(e)}")
                continue
        
        # Remove duplicates based on content hash
        unique_articles = self._remove_duplicates(all_articles)
        
        logger.info(f"Total unique conflict articles: {len(unique_articles)}")
        return unique_articles

    def _scrape_source(self, source_key: str, source_config: Dict[str, Any], hours_back: int) -> List[Dict[str, Any]]:
        """Scrape articles from a single source"""
        articles = []
        
        try:
            # Fetch RSS feed
            response = self.session.get(source_config['rss_url'], timeout=30)
            response.raise_for_status()
            
            # Parse RSS feed
            feed = feedparser.parse(response.content)
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
            
            for entry in feed.entries:
                try:
                    # Parse publication date
                    pub_date = self._parse_date(entry.get('published', ''))
                    
                    # Skip if too old
                    if pub_date and pub_date < cutoff_time:
                        continue
                    
                    # Extract basic article info
                    article = {
                        'title': entry.get('title', '').strip(),
                        'url': entry.get('link', '').strip(),
                        'summary': entry.get('summary', '').strip(),
                        'published_date': pub_date.isoformat() if pub_date else None,
                        'raw_data': entry
                    }
                    
                    # Generate unique hash
                    article['content_hash'] = hashlib.md5(
                        f"{article['title']}{article['url']}".encode()
                    ).hexdigest()
                    
                    # Scrape full article content
                    full_content = self._scrape_full_article(article['url'], source_config)
                    if full_content:
                        article['content'] = full_content
                        articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error processing article: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping RSS feed for {source_key}: {str(e)}")
        
        return articles

    def _scrape_full_article(self, url: str, source_config: Dict[str, Any]) -> Optional[str]:
        """Scrape full article content"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'advertisement']):
                element.decompose()
            
            # Try different content selectors based on source
            content_selectors = [
                'article', '.entry-content', '.post-content', '.article-body',
                '.content', 'main', '.post-body', '.story-content', '.entry-summary'
            ]
            
            content = ''
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(strip=True)
                    break
            
            # Fallback to body if no content found
            if not content:
                content = soup.get_text(strip=True)
            
            # Clean up content
            content = re.sub(r'\s+', ' ', content)
            content = content.strip()
            
            # Only return if substantial content
            if len(content) > 100:
                return content
            
        except Exception as e:
            logger.error(f"Error scraping full article {url}: {str(e)}")
        
        return None

    def _filter_conflict_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter articles that contain conflict-related content"""
        conflict_articles = []
        
        for article in articles:
            text_to_check = f"{article['title']} {article['summary']} {article.get('content', '')}".lower()
            
            # Check for conflict keywords
            has_conflict_keyword = any(keyword in text_to_check for keyword in self.conflict_keywords)
            
            # Check for Nigerian locations
            has_nigerian_location = any(state in text_to_check for state in self.nigerian_states)
            
            # Additional quality checks
            has_substantial_content = len(article.get('content', '')) > 200
            has_meaningful_title = len(article['title']) > 10
            
            if (has_conflict_keyword and has_nigerian_location and 
                has_substantial_content and has_meaningful_title):
                
                # Extract detected keywords and locations
                article['is_conflict_related'] = True
                article['detected_keywords'] = [
                    kw for kw in self.conflict_keywords if kw in text_to_check
                ]
                article['detected_locations'] = [
                    loc for loc in self.nigerian_states if loc in text_to_check
                ]
                
                conflict_articles.append(article)
        
        return conflict_articles

    def _remove_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate articles based on content hash"""
        seen_hashes = set()
        unique_articles = []
        
        for article in articles:
            if article['content_hash'] not in seen_hashes:
                seen_hashes.add(article['content_hash'])
                unique_articles.append(article)
        
        return unique_articles

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string into datetime object"""
        if not date_str:
            return None
        
        try:
            # Handle common date formats
            date_formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%SZ',
                '%a, %d %b %Y %H:%M:%S %z',
                '%a, %d %b %Y %H:%M:%S GMT',
                '%a, %d %b %Y %H:%M:%S %Z'
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    # Remove timezone info to avoid comparison issues
                    if parsed_date.tzinfo:
                        parsed_date = parsed_date.replace(tzinfo=None)
                    return parsed_date
                except ValueError:
                    continue
            
            # Try parsing with timezone and remove it
            try:
                from dateutil import parser
                parsed_date = parser.parse(date_str)
                if parsed_date.tzinfo:
                    parsed_date = parsed_date.replace(tzinfo=None)
                return parsed_date
            except:
                pass
            
            # Handle relative dates like "2 hours ago"
            if 'ago' in date_str.lower():
                # Simple heuristic - assume recent
                return datetime.utcnow() - timedelta(hours=2)
            
        except Exception as e:
            logger.error(f"Error parsing date '{date_str}': {str(e)}")
        
        return None

    def get_article_for_extraction(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare article for NLP extraction
        
        Args:
            article: Raw article data
            
        Returns:
            Article data formatted for extraction
        """
        return {
            'text': article.get('content', article.get('summary', '')),
            'title': article['title'],
            'url': article['url'],
            'source': article['source_key'],
            'published_date': article['published_date'],
            'quality_score': article['source_quality'],
            'detected_keywords': article.get('detected_keywords', []),
            'detected_locations': article.get('detected_locations', [])
        }

    def scrape_source_by_keyword(self, source_key: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """Scrape specific source for articles containing keywords"""
        if source_key not in self.target_sources:
            raise ValueError(f"Unknown source: {source_key}")
        
        source_config = self.target_sources[source_key]
        articles = self._scrape_source(source_key, source_config, 24)  # Last 24 hours
        
        # Filter by keywords
        filtered_articles = []
        for article in articles:
            text = f"{article['title']} {article.get('content', '')}".lower()
            if any(keyword.lower() in text for keyword in keywords):
                filtered_articles.append(article)
        
        return filtered_articles

# Example usage
if __name__ == "__main__":
    scraper = TargetedNewsScraper()
    
    # Scrape recent articles
    articles = scraper.scrape_recent_articles(hours_back=6)
    
    for article in articles[:3]:  # Show first 3
        print(f"Title: {article['title']}")
        print(f"Source: {article['source_key']}")
        print(f"Keywords: {article.get('detected_keywords', [])}")
        print(f"Locations: {article.get('detected_locations', [])}")
        print("-" * 50)
