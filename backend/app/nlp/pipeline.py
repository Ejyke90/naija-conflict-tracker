"""
Complete NLP Event Extraction Pipeline
Orchestrates scraping, extraction, geocoding, and verification
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from app.nlp.news_scraper import TargetedNewsScraper
from app.nlp.rss_fetcher import RSSNewsFetcher
from app.nlp.groq_extractor import GroqEventExtractor
from app.nlp.geocoding import NigerianGeocoder
from app.nlp.verification import EventVerificationSystem

logger = logging.getLogger(__name__)

class NLPEventExtractionPipeline:
    """Complete pipeline for extracting conflict events from news"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Get absolute path to data directory
        current_dir = Path(__file__).parent.parent.parent
        data_dir = current_dir / 'data'
        
        # Initialize components
        self.scraper = TargetedNewsScraper()
        self.rss_fetcher = RSSNewsFetcher()
        self.extractor = GroqEventExtractor()
        self.geocoder = NigerianGeocoder(data_dir=str(data_dir))
        self.verifier = EventVerificationSystem(self.geocoder)
        
        # Pipeline configuration
        self.max_articles_per_run = self.config.get('max_articles', 50)
        self.confidence_threshold = self.config.get('confidence_threshold', 0.70)
        self.output_dir = Path(self.config.get('output_dir', str(data_dir / 'extracted_events')))
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Statistics
        self.stats = {
            'articles_scraped': 0,
            'events_extracted': 0,
            'events_verified': 0,
            'auto_published': 0,
            'pending_verification': 0,
            'rejected': 0,
            'errors': 0
        }

    def run_pipeline(self, hours_back: int = 6) -> Dict[str, Any]:
        """
        Run the complete NLP extraction pipeline
        
        Args:
            hours_back: Number of hours to look back for articles
            
        Returns:
            Pipeline results and statistics
        """
        logger.info(f"Starting NLP Event Extraction Pipeline for last {hours_back} hours")
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Fetch articles from RSS feeds
            logger.info("Step 1: Fetching articles from RSS feeds...")
            
            # Load previously seen GUIDs to avoid duplicates
            self.rss_fetcher.load_seen_guids()
            
            # Fetch from RSS feeds (prioritize Nigerian sources)
            articles = self.rss_fetcher.fetch_all_feeds(
                regions=['nigerian', 'international', 'specialized'],
                max_priority=2,
                delay_between=1.0
            )
            
            # Filter for recent articles
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
            recent_articles = [
                a for a in articles 
                if a.get('published_datetime', datetime.min) >= cutoff_time
            ]
            
            # Save seen GUIDs for next run
            self.rss_fetcher.save_seen_guids()
            
            self.stats['articles_scraped'] = len(recent_articles)
            articles = recent_articles
            
            if not articles:
                logger.warning("No articles found to process")
                return self._generate_pipeline_report(start_time)
            
            # Limit articles to prevent excessive API calls
            if len(articles) > self.max_articles_per_run:
                articles = articles[:self.max_articles_per_run]
                logger.info(f"Limited to {self.max_articles_per_run} articles")
            
            # Step 2: Extract events using Groq
            logger.info("Step 2: Extracting events with Groq Llama 3...")
            extraction_results = self.extractor.batch_extract(articles)
            extracted_events = extraction_results['events']
            self.stats['events_extracted'] = len(extracted_events)
            
            if not extracted_events:
                logger.warning("No events extracted from articles")
                return self._generate_pipeline_report(start_time)
            
            # Step 3: Geocode locations
            logger.info("Step 3: Geocoding event locations...")
            # Convert ExtractedEvent objects to dictionaries
            extracted_events_dict = [event.dict() for event in extracted_events]
            geocoded_events = self._geocode_events(extracted_events_dict)
            
            # Step 4: Verify events
            logger.info("Step 4: Verifying events...")
            verification_results = self.verifier.batch_verify_events(geocoded_events)
            verified_events = verification_results['events']
            
            # Update statistics
            for result in verified_events:
                status = result['verification_status']
                if status == 'auto_publish':
                    self.stats['auto_published'] += 1
                elif status == 'pending_verification':
                    self.stats['pending_verification'] += 1
                elif status in ['reject', 'location_missing', 'date_missing']:
                    self.stats['rejected'] += 1
                else:
                    self.stats['pending_verification'] += 1
            
            self.stats['events_verified'] = len(verified_events)
            
            # Step 5: Save results
            logger.info("Step 5: Saving results...")
            self._save_results(verified_events, articles)
            
            # Step 6: Generate report
            report = self._generate_pipeline_report(start_time)
            
            logger.info(f"Pipeline completed successfully")
            logger.info(f"Extracted {self.stats['events_extracted']} events from {self.stats['articles_scraped']} articles")
            logger.info(f"Auto-published: {self.stats['auto_published']}, Pending: {self.stats['pending_verification']}")
            
            return report
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            self.stats['errors'] += 1
            return {
                'status': 'failed',
                'error': str(e),
                'stats': self.stats,
                'duration': (datetime.utcnow() - start_time).total_seconds()
            }

    def _extract_events_from_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract events from articles using Groq"""
        extracted_events = []
        
        for i, article in enumerate(articles):
            try:
                logger.info(f"Extracting from article {i+1}/{len(articles)}: {article['title'][:50]}...")
                
                # Prepare article text
                article_text = self.scraper.get_article_for_extraction(article)
                text = article_text['text']
                
                if len(text) < 100:
                    logger.warning(f"Article too short, skipping: {article['url']}")
                    continue
                
                # Extract event using Groq
                extracted_event = self.extractor.extract_event(text, article['url'])
                
                if extracted_event:
                    # Add metadata
                    extracted_event_dict = extracted_event.dict()
                    extracted_event_dict['scraped_metadata'] = {
                        'source': article_text['source'],
                        'quality_score': article_text['quality_score'],
                        'detected_keywords': article_text['detected_keywords'],
                        'detected_locations': article_text['detected_locations']
                    }
                    extracted_events.append(extracted_event_dict)
                    logger.info(f"Successfully extracted event: {extracted_event.crisis_type}")
                else:
                    logger.warning(f"Failed to extract event from: {article['url']}")
                
            except Exception as e:
                logger.error(f"Error extracting from article {i+1}: {str(e)}")
                self.stats['errors'] += 1
                continue
        
        return extracted_events

    def _geocode_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Geocode all extracted events"""
        geocoded_events = []
        
        for event in events:
            try:
                # Geocode location
                geo_result = self.geocoder.geocode_location(event['location'])
                
                if geo_result:
                    event['geocoded_location'] = geo_result
                    geocoded_events.append(event)
                else:
                    logger.warning(f"Failed to geocode location: {event['location']}")
                    # Still include event but mark geocoding as failed
                    event['geocoded_location'] = None
                    geocoded_events.append(event)
                
            except Exception as e:
                logger.error(f"Error geocoding event: {str(e)}")
                event['geocoded_location'] = None
                geocoded_events.append(event)
        
        return geocoded_events

    def _save_results(self, verified_events: List[Dict[str, Any]], articles: List[Dict[str, Any]]):
        """Save pipeline results to files"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        # Save verified events
        events_file = self.output_dir / f"events_{timestamp}.json"
        with open(events_file, 'w') as f:
            json.dump(verified_events, f, indent=2, default=str)
        
        # Save raw articles for reference
        articles_file = self.output_dir / f"articles_{timestamp}.json"
        with open(articles_file, 'w') as f:
            json.dump(articles, f, indent=2, default=str)
        
        # Save summary
        summary_file = self.output_dir / f"summary_{timestamp}.json"
        summary = {
            'timestamp': timestamp,
            'stats': self.stats,
            'events_by_status': {
                'auto_publish': [e for e in verified_events if e['verification_status'] == 'auto_publish'],
                'pending_verification': [e for e in verified_events if e['verification_status'] == 'pending_verification'],
                'rejected': [e for e in verified_events if e['verification_status'] in ['reject', 'location_missing', 'date_missing']]
            }
        }
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Results saved to {events_file}")

    def _generate_pipeline_report(self, start_time: datetime) -> Dict[str, Any]:
        """Generate comprehensive pipeline report"""
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        return {
            'status': 'completed',
            'timestamp': datetime.utcnow().isoformat(),
            'duration_seconds': duration,
            'stats': self.stats,
            'success_rate': (self.stats['events_verified'] / max(self.stats['events_extracted'], 1)) * 100,
            'auto_publish_rate': (self.stats['auto_published'] / max(self.stats['events_verified'], 1)) * 100,
            'output_files': list(self.output_dir.glob(f"*_{datetime.utcnow().strftime('%Y%m%d')}_*.json"))
        }

    def get_events_for_database(self, min_confidence: float = 0.85) -> List[Dict[str, Any]]:
        """
        Get events ready for database insertion
        
        Args:
            min_confidence: Minimum confidence score for database insertion
            
        Returns:
            List of events formatted for database
        """
        # Find latest results file
        latest_files = sorted(self.output_dir.glob("events_*.json"), reverse=True)
        
        if not latest_files:
            return []
        
        with open(latest_files[0], 'r') as f:
            events = json.load(f)
        
        # Filter and format for database
        db_events = []
        
        for event_data in events:
            verification = event_data.get('verification_result', {})
            
            if verification.get('confidence_score', 0) >= min_confidence:
                db_event = {
                    'incident_date': event_data['incident_date'],
                    'location': event_data['geocoded_location'],
                    'crisis_type': event_data['crisis_type'],
                    'actor_primary': event_data['actor_primary'],
                    'actor_secondary': event_data.get('actor_secondary'),
                    'fatalities': event_data['fatalities'],
                    'injuries': event_data.get('injuries'),
                    'source_url': event_data['source_url'],
                    'confidence_score': verification['confidence_score'],
                    'verification_status': verification['verification_status'],
                    'raw_text': event_data['raw_text'],
                    'extracted_at': datetime.utcnow().isoformat()
                }
                db_events.append(db_event)
        
        return db_events

    def run_single_article_extraction(self, article_url: str) -> Optional[Dict[str, Any]]:
        """
        Extract event from a single article URL
        Useful for testing or manual extraction
        
        Args:
            article_url: URL of article to extract from
            
        Returns:
            Extracted and verified event or None
        """
        try:
            logger.info(f"Extracting from single article: {article_url}")
            
            # Scrape single article
            # This would need to be implemented in the scraper
            # For now, return placeholder
            return {
                'status': 'single_article_extraction',
                'url': article_url,
                'message': 'Single article extraction not yet implemented'
            }
            
        except Exception as e:
            logger.error(f"Error extracting from single article: {str(e)}")
            return None

# Configuration for different environments
def get_pipeline_config(environment: str = 'production') -> Dict[str, Any]:
    """Get pipeline configuration for environment"""
    
    configs = {
        'development': {
            'max_articles': 10,
            'confidence_threshold': 0.60,
            'output_dir': 'data/dev_events'
        },
        'staging': {
            'max_articles': 25,
            'confidence_threshold': 0.75,
            'output_dir': 'data/staging_events'
        },
        'production': {
            'max_articles': 50,
            'confidence_threshold': 0.85,
            'output_dir': 'data/prod_events'
        }
    }
    
    return configs.get(environment, configs['production'])

def main():
    """Main entry point for pipeline execution"""
    import sys
    
    # Get environment from args or env var
    environment = os.getenv('ENVIRONMENT', 'production')
    hours_back = int(os.getenv('HOURS_BACK', '6'))
    
    if len(sys.argv) > 1:
        environment = sys.argv[1]
    if len(sys.argv) > 2:
        hours_back = int(sys.argv[2])
    
    print(f"Running pipeline in {environment} mode (last {hours_back} hours)")
    
    # Validate required environment variables
    required_vars = ['GROQ_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    try:
        # Get configuration
        config = get_pipeline_config(environment)
        config['max_articles'] = 20  # Conservative for GitHub Actions
        
        # Initialize and run pipeline
        pipeline = NLPEventExtractionPipeline(config)
        results = pipeline.run_pipeline(hours_back=hours_back)
        
        # Print results
        print('=== NLP EXTRACTION RESULTS ===')
        print(json.dumps(results, indent=2, default=str))
        
        # Save results to file for GitHub Actions
        with open('pipeline_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Exit with error if pipeline failed
        if results.get('status') == 'failed':
            print('Pipeline failed!')
            sys.exit(1)
            
    except Exception as e:
        print(f'ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        
        # Create minimal results file even on failure
        error_results = {
            "status": "failed",
            "error": str(e),
            "stats": {
                "articles_scraped": 0,
                "events_extracted": 0,
                "events_verified": 0,
                "auto_published": 0,
                "pending_verification": 0,
                "rejected": 0
            }
        }
        
        with open('pipeline_results.json', 'w') as f:
            json.dump(error_results, f, indent=2)
        
        sys.exit(1)

# Example usage
if __name__ == "__main__":
    main()
