from celery import current_task
from app.core.celery_app import celery_app
import requests
import feedparser
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import re
from datetime import datetime, timedelta
import logging
from urllib.parse import urljoin, urlparse
import time
import hashlib

logger = logging.getLogger(__name__)

# Nigerian news sources configuration
NIGERIAN_NEWS_SOURCES = {
    'punch': {
        'name': 'Punch Newspapers',
        'rss_url': 'https://punchng.com/feed/',
        'base_url': 'https://punchng.com',
        'regions': ['national', 'metro', 'south-west', 'south-south', 'south-east', 'north']
    },
    'vanguard': {
        'name': 'Vanguard News',
        'rss_url': 'https://www.vanguardngr.com/feed/',
        'base_url': 'https://www.vanguardngr.com',
        'regions': ['national', 'politics', 'metro', 'south-south', 'south-east', 'north']
    },
    'daily_trust': {
        'name': 'Daily Trust',
        'rss_url': 'https://www.dailytrust.com.ng/feed/',
        'base_url': 'https://www.dailytrust.com.ng',
        'regions': ['national', 'north', 'north-west', 'north-east']
    },
    'guardian': {
        'name': 'Guardian Nigeria',
        'rss_url': 'https://guardian.ng/feed/',
        'base_url': 'https://guardian.ng',
        'regions': ['national', 'politics', 'metro', 'south-west', 'south-south']
    },
    'thisday': {
        'name': 'ThisDay Live',
        'rss_url': 'https://www.thisdaylive.com/index.php/feed/',
        'base_url': 'https://www.thisdaylive.com',
        'regions': ['national', 'politics', 'metro', 'south-south', 'north']
    },
    'leadership': {
        'name': 'Leadership Newspaper',
        'rss_url': 'https://leadership.ng/feed/',
        'base_url': 'https://leadership.ng',
        'regions': ['national', 'politics', 'metro', 'north', 'south-south']
    },
    'sun': {
        'name': 'The Sun Nigeria',
        'rss_url': 'https://www.sunnewsonline.com/feed/',
        'base_url': 'https://www.sunnewsonline.com',
        'regions': ['national', 'metro', 'south-east', 'south-south']
    },
    'tribune': {
        'name': 'Nigerian Tribune',
        'rss_url': 'https://tribuneonlineng.com/feed/',
        'base_url': 'https://tribuneonlineng.com',
        'regions': ['national', 'politics', 'south-west', 'south-east']
    },
    'independent': {
        'name': 'Independent Newspapers',
        'rss_url': 'https://independent.ng/feed/',
        'base_url': 'https://independent.ng',
        'regions': ['national', 'politics', 'metro', 'south-west', 'north']
    },
    'nation': {
        'name': 'The Nation Newspaper',
        'rss_url': 'https://thenationonlineng.net/feed/',
        'base_url': 'https://thenationonlineng.net',
        'regions': ['national', 'politics', 'metro', 'south-west', 'south-south']
    },
    'channelstv': {
        'name': 'Channels Television',
        'rss_url': 'https://www.channelstv.com/feed/',
        'base_url': 'https://www.channelstv.com',
        'regions': ['national', 'politics', 'metro', 'north', 'south-south']
    },
    'premiumtimes': {
        'name': 'Premium Times',
        'rss_url': 'https://www.premiumtimesng.com/feed/',
        'base_url': 'https://www.premiumtimesng.com',
        'regions': ['national', 'investigations', 'north', 'south-south', 'south-east']
    },
    'saharareporters': {
        'name': 'Sahara Reporters',
        'rss_url': 'https://saharareporters.com/feed/',
        'base_url': 'https://saharareporters.com',
        'regions': ['national', 'politics', 'metro', 'north', 'south-south']
    },
    'daily_post': {
        'name': 'Daily Post Nigeria',
        'rss_url': 'https://dailypost.ng/feed/',
        'base_url': 'https://dailypost.ng',
        'regions': ['national', 'politics', 'metro', 'south-west', 'south-east', 'north']
    },
    'nigerian_info': {
        'name': 'Nigerian Tribune',
        'rss_url': 'https://www.nigerianinf Tribune.com/feed/',
        'base_url': 'https://www.nigerianinf Tribune.com',
        'regions': ['national', 'politics', 'metro', 'north', 'south-south']
    }
}

# Conflict-related keywords for filtering
CONFLICT_KEYWORDS = [
    'conflict', 'violence', 'attack', 'killed', 'dead', 'fatalities', 'casualties',
    'kidnapping', 'abduction', 'bandit', 'terrorist', 'boko haram', 'ipob', 'unknown gunmen',
    'clash', 'communal', 'ethnic', 'religious', 'herders', 'farmers', 'cattle rustling',
    'militant', 'insurgency', 'security', 'military', 'police', 'army', 'shooting',
    'bomb', 'explosion', 'armed', 'gunmen', 'robbery', 'raid', 'invasion',
    'displacement', 'refugees', 'crisis', 'unrest', 'protest', 'riot', 'curfew'
]

# Location keywords for Nigerian states and major cities
NIGERIAN_LOCATIONS = {
    'states': [
        'abia', 'adamawa', 'akwa ibom', 'anambra', 'bauchi', 'bayelsa', 'benue', 'borno',
        'cross river', 'delta', 'ebonyi', 'edo', 'ekiti', 'enugu', 'gombe', 'imo',
        'jigawa', 'kaduna', 'kano', 'katsina', 'kebbi', 'kogi', 'kwara', 'lagos',
        'nasarawa', 'niger', 'ogun', 'ondo', 'osun', 'oyo', 'plateau', 'rivers',
        'sokoto', 'taraba', 'yobe', 'zamfara', 'fct', 'abuja'
    ],
    'major_cities': [
        'lagos', 'abuja', 'kano', 'ibadan', 'kaduna', 'port harcourt', 'benin city',
        'maiduguri', 'zaria', 'aba', 'jos', 'ilorin', 'oyo', 'enugu', 'aba',
        'onitsha', 'warri', 'akure', 'makurdi', 'sokoto', 'calabar', 'uyo', 'asaba',
        'awka', 'ilorin', 'ikeja', 'katsina', 'minna', 'bauchi', 'gusau', 'damaturu',
        'jalingo', 'birnin kebbi', 'dutse', 'lokoja', 'yingi', 'kafanchan', 'otukpo'
    ]
}

class NewsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def scrape_rss_feed(self, source_key: str, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape articles from RSS feed"""
        articles = []
        try:
            # Fetch RSS feed
            response = self.session.get(source_config['rss_url'], timeout=30)
            response.raise_for_status()
            
            # Parse RSS feed
            feed = feedparser.parse(response.content)
            
            for entry in feed.entries:
                article = {
                    'source': source_key,
                    'source_name': source_config['name'],
                    'title': entry.get('title', ''),
                    'url': entry.get('link', ''),
                    'published_date': entry.get('published', ''),
                    'summary': entry.get('summary', ''),
                    'content': '',  # Will be populated by full article scrape
                    'scraped_at': datetime.utcnow().isoformat(),
                    'raw_data': entry
                }
                
                # Generate unique hash for deduplication
                article['hash'] = hashlib.md5(
                    f"{article['title']}{article['url']}".encode()
                ).hexdigest()
                
                articles.append(article)
                
        except Exception as e:
            logger.error(f"Error scraping RSS feed for {source_key}: {str(e)}")
            
        return articles

    def scrape_full_article(self, article: Dict[str, Any], source_config: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape full article content"""
        try:
            response = self.session.get(article['url'], timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Extract main content (common selectors)
            content_selectors = [
                'article', '.entry-content', '.post-content', '.article-body',
                '.content', 'main', '.post-body', '.story-content'
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
            
            article['content'] = content
            article['full_scraped_at'] = datetime.utcnow().isoformat()
            
        except Exception as e:
            logger.error(f"Error scraping full article {article['url']}: {str(e)}")
            
        return article

    def filter_conflict_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter articles that contain conflict-related keywords"""
        conflict_articles = []
        
        for article in articles:
            text_to_check = f"{article['title']} {article['summary']} {article['content']}".lower()
            
            # Check for conflict keywords
            has_conflict_keyword = any(keyword in text_to_check for keyword in CONFLICT_KEYWORDS)
            
            # Check for Nigerian locations
            has_nigerian_location = any(
                location in text_to_check for location in 
                NIGERIAN_LOCATIONS['states'] + NIGERIAN_LOCATIONS['major_cities']
            )
            
            if has_conflict_keyword and has_nigerian_location:
                article['is_conflict_related'] = True
                article['detected_keywords'] = [
                    kw for kw in CONFLICT_KEYWORDS if kw in text_to_check
                ]
                article['detected_locations'] = [
                    loc for loc in NIGERIAN_LOCATIONS['states'] + NIGERIAN_LOCATIONS['major_cities'] 
                    if loc in text_to_check
                ]
                conflict_articles.append(article)
            else:
                article['is_conflict_related'] = False
                
        return conflict_articles

@celery_app.task(bind=True, name='app.tasks.scraping_tasks.scrape_news_source')
def scrape_news_source(self, source_key: str):
    """Scrape a single news source"""
    try:
        # Update task status
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 1, 'status': f'Scraping {source_key}'}
        )
        
        source_config = NIGERIAN_NEWS_SOURCES.get(source_key)
        if not source_config:
            raise ValueError(f"Unknown news source: {source_key}")
        
        scraper = NewsScraper()
        
        # Scrape RSS feed
        articles = scraper.scrape_rss_feed(source_key, source_config)
        
        # Scrape full articles for recent ones (last 24 hours)
        recent_articles = []
        cutoff_date = datetime.utcnow() - timedelta(hours=24)
        
        for article in articles:
            try:
                pub_date = datetime.fromisoformat(article['published_date'].replace('Z', '+00:00'))
                if pub_date > cutoff_date:
                    full_article = scraper.scrape_full_article(article, source_config)
                    recent_articles.append(full_article)
            except:
                # If date parsing fails, include the article anyway
                full_article = scraper.scrape_full_article(article, source_config)
                recent_articles.append(full_article)
        
        # Filter conflict-related articles
        conflict_articles = scraper.filter_conflict_articles(recent_articles)
        
        # Update task status
        self.update_state(
            state='SUCCESS',
            meta={
                'current': 1, 'total': 1,
                'status': f'Completed {source_key}',
                'articles_found': len(articles),
                'conflict_articles': len(conflict_articles)
            }
        )
        
        return {
            'source': source_key,
            'total_articles': len(articles),
            'conflict_articles': len(conflict_articles),
            'articles': conflict_articles,
            'scraped_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in scrape_news_source task for {source_key}: {str(e)}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'source': source_key}
        )
        raise

@celery_app.task(bind=True, name='app.tasks.scraping_tasks.scrape_all_news_sources')
def scrape_all_news_sources(self):
    """Scrape all configured Nigerian news sources"""
    try:
        task_id = self.request.id
        total_sources = len(NIGERIAN_NEWS_SOURCES)
        results = []
        
        logger.info(f"Starting scraping of {total_sources} news sources")
        
        # Update initial status
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': total_sources, 'status': 'Starting news scraping'}
        )
        
        for i, source_key in enumerate(NIGERIAN_NEWS_SOURCES.keys()):
            try:
                # Scrape individual source
                result = scrape_news_source.delay(source_key)
                results.append(result)
                
                # Update progress
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': i + 1, 
                        'total': total_sources,
                        'status': f'Completed {i + 1}/{total_sources} sources'
                    }
                )
                
                # Small delay to be respectful to servers
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Failed to scrape {source_key}: {str(e)}")
                continue
        
        # Wait for all tasks to complete and collect results
        final_results = []
        for result in results:
            try:
                final_results.append(result.get(timeout=300))  # 5 minute timeout per source
            except Exception as e:
                logger.error(f"Failed to get result from scraping task: {str(e)}")
        
        # Aggregate statistics
        total_articles = sum(r['total_articles'] for r in final_results)
        total_conflict_articles = sum(r['conflict_articles'] for r in final_results)
        all_conflict_articles = []
        
        for result in final_results:
            all_conflict_articles.extend(result.get('articles', []))
        
        # Update final status
        self.update_state(
            state='SUCCESS',
            meta={
                'current': total_sources,
                'total': total_sources,
                'status': 'All sources scraped successfully',
                'total_articles': total_articles,
                'conflict_articles': total_conflict_articles,
                'sources_completed': len(final_results)
            }
        )
        
        logger.info(f"Scraping completed: {total_articles} total articles, {total_conflict_articles} conflict-related")
        
        return {
            'task_id': task_id,
            'scraped_at': datetime.utcnow().isoformat(),
            'sources_scraped': len(final_results),
            'total_articles': total_articles,
            'conflict_articles': total_conflict_articles,
            'articles': all_conflict_articles,
            'sources': [r['source'] for r in final_results]
        }
        
    except Exception as e:
        logger.error(f"Error in scrape_all_news_sources task: {str(e)}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise

@celery_app.task(bind=True, name='app.tasks.scraping_tasks.scrape_source_by_region')
def scrape_source_by_region(self, source_key: str, region: str):
    """Scrape a specific news source filtered by region"""
    try:
        source_config = NIGERIAN_NEWS_SOURCES.get(source_key)
        if not source_config:
            raise ValueError(f"Unknown news source: {source_key}")
        
        if region not in source_config['regions']:
            raise ValueError(f"Region {region} not available for {source_key}")
        
        # This would be implemented to filter articles by region
        # For now, it returns all articles from the source
        result = scrape_news_source.delay(source_key)
        return result.get()
        
    except Exception as e:
        logger.error(f"Error in scrape_source_by_region task: {str(e)}")
        raise

@celery_app.task(bind=True, name='app.tasks.scraping_tasks.emergency_scrape')
def emergency_scrape(self, keywords: List[str]):
    """Emergency scraping for specific keywords (e.g., major incidents)"""
    try:
        # This would implement targeted scraping for breaking news
        # For now, it triggers a full scrape
        result = scrape_all_news_sources.delay()
        return result.get()
        
    except Exception as e:
        logger.error(f"Error in emergency_scrape task: {str(e)}")
        raise
