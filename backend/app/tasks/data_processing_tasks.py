from celery import current_task
from app.core.celery_app import celery_app
from app.db.database import get_db
from app.models.conflict import Conflict
from app.models.location import Location
from app.models.actor import Actor
from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_, or_
from typing import List, Dict, Any, Optional, Tuple
import re
import spacy
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from datetime import datetime, timedelta
import logging
import hashlib
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

# Load spaCy model for NLP processing
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("spaCy model not found. Using basic text processing.")
    nlp = None

# Initialize geocoder
geolocator = Nominatim(user_agent="naija_conflict_tracker")

# Nigerian states and their capitals for location validation
NIGERIAN_STATES = {
    'abia': 'umuahia', 'adamawa': 'yola', 'akwa ibom': 'uyo', 'anambra': 'awka',
    'bauchi': 'bauchi', 'bayelsa': 'yenagoa', 'benue': 'makurdi', 'borno': 'maiduguri',
    'cross river': 'calabar', 'delta': 'asaba', 'ebonyi': 'abakaliki', 'edo': 'benin city',
    'ekiti': 'ado ekiti', 'enugu': 'enugu', 'gombe': 'gombe', 'imo': 'owerri',
    'jigawa': 'dutse', 'kaduna': 'kaduna', 'kano': 'kano', 'katsina': 'katsina',
    'kebbi': 'birnin kebbi', 'kogi': 'lokoja', 'kwara': 'ilorin', 'lagos': 'ikeja',
    'nasarawa': 'karu', 'niger': 'minna', 'ogun': 'abeokuta', 'ondo': 'akure',
    'osun': 'osogbo', 'oyo': 'ibadan', 'plateau': 'jos', 'rivers': 'port harcourt',
    'sokoto': 'sokoto', 'taraba': 'jalingo', 'yobe': 'damaturu', 'zamfara': 'gusau',
    'fct': 'abuja'
}

# Conflict event types classification
CONFLICT_EVENT_TYPES = {
    'armed_conflict': ['attack', 'clash', 'gunfight', 'battle', 'confrontation'],
    'terrorism': ['bomb', 'explosion', 'suicide', 'boko haram', 'terrorist'],
    'kidnapping': ['kidnap', 'abduction', 'hostage', 'ransom'],
    'communal_violence': ['communal', 'ethnic', 'religious', 'clash'],
    'banditry': ['bandit', 'robbery', 'raid', 'cattle rustling'],
    'political_violence': ['election', 'political', 'rally', 'protest'],
    'security_operations': ['military', 'police', 'security', 'operation'],
    'protest': ['protest', 'demonstration', 'riot', 'curfew'],
    'unknown': ['unknown gunmen', 'unidentified', 'mysterious']
}

class DataProcessor:
    def __init__(self):
        self.processed_count = 0
        self.errors = []

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s.,!?;:()-]', '', text)
        
        # Convert to lowercase for processing
        return text.strip().lower()

    def extract_date(self, text: str, published_date: str = None) -> Optional[datetime]:
        """Extract and normalize date from text"""
        if published_date:
            try:
                # Try to parse published date first
                if 'ago' in published_date.lower():
                    # Handle relative dates like "2 hours ago"
                    return datetime.utcnow() - timedelta(hours=2)
                return datetime.fromisoformat(published_date.replace('Z', '+00:00'))
            except:
                pass
        
        # Extract dates from text using regex
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY or MM/DD/YYYY
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD or YYYY-DD-MM
            r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',        # January 15, 2024
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    # Simple date parsing - would need more sophisticated logic
                    return datetime.strptime(match.group(0), "%Y-%m-%d")
                except:
                    continue
        
        return None

    def extract_fatalities(self, text: str) -> Tuple[int, int]:
        """Extract number of killed and injured from text"""
        killed = injured = 0
        
        # Patterns for fatalities
        killed_patterns = [
            r'(\d+)\s+killed',
            r'(\d+)\s+dead',
            r'(\d+)\s+fatalities',
            r'(\d+)\s+died',
            r'death\s+of\s+(\d+)',
        ]
        
        # Patterns for injuries
        injured_patterns = [
            r'(\d+)\s+injured',
            r'(\d+)\s+hurt',
            r'(\d+)\s+wounded',
        ]
        
        for pattern in killed_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                killed = max(killed, int(match.group(1)))
        
        for pattern in injured_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                injured = max(injured, int(match.group(1)))
        
        return killed, injured

    def classify_event_type(self, text: str) -> str:
        """Classify the type of conflict event"""
        text_lower = text.lower()
        
        for event_type, keywords in CONFLICT_EVENT_TYPES.items():
            if any(keyword in text_lower for keyword in keywords):
                return event_type
        
        return 'unknown'

    def extract_locations(self, text: str) -> List[str]:
        """Extract Nigerian locations from text"""
        locations = []
        text_lower = text.lower()
        
        # Check for states
        for state in NIGERIAN_STATES.keys():
            if state in text_lower:
                locations.append(state.title())
        
        # Check for major cities
        major_cities = [
            'lagos', 'abuja', 'kano', 'ibadan', 'kaduna', 'port harcourt',
            'benin city', 'maiduguri', 'zaria', 'aba', 'jos', 'ilorin',
            'enugu', 'aba', 'onitsha', 'warri', 'akure', 'makurdi'
        ]
        
        for city in major_cities:
            if city in text_lower:
                locations.append(city.title())
        
        # Use spaCy for named entity recognition if available
        if nlp:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['GPE', 'LOC']:  # Geographical entities
                    locations.append(ent.text)
        
        return list(set(locations))  # Remove duplicates

    def geocode_location(self, location: str) -> Optional[Dict[str, Any]]:
        """Geocode location to get coordinates"""
        try:
            # Add Nigeria to improve geocoding accuracy
            query = f"{location}, Nigeria"
            
            result = geolocator.geocode(query, timeout=10)
            if result:
                return {
                    'name': location,
                    'latitude': result.latitude,
                    'longitude': result.longitude,
                    'address': result.address,
                    'confidence': result.raw.get('importance', 0)
                }
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.warning(f"Geocoding failed for {location}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error geocoding {location}: {str(e)}")
        
        return None

    def extract_actors(self, text: str) -> List[str]:
        """Extract conflict actors from text"""
        actors = []
        text_lower = text.lower()
        
        # Known actor patterns
        actor_patterns = {
            'boko haram': ['boko haram', 'jihadists', 'insurgents'],
            'ipob': ['ipob', 'indigenous people of biafra', 'biafran'],
            'bandits': ['bandits', 'gunmen', 'unknown gunmen'],
            'military': ['military', 'army', 'soldiers', 'troops'],
            'police': ['police', 'security forces', 'officers'],
            'herders': ['herders', 'fulani herders', 'pastoralists'],
            'farmers': ['farmers', 'villagers', 'community'],
            'political': ['politicians', 'supporters', 'thugs']
        }
        
        for actor, keywords in actor_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                actors.append(actor.title())
        
        return list(set(actors))

    def generate_content_hash(self, article: Dict[str, Any]) -> str:
        """Generate hash for content deduplication"""
        content = f"{article.get('title', '')}{article.get('content', '')}"
        return hashlib.md5(content.encode()).hexdigest()

    def validate_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and score article quality"""
        score = 0
        issues = []
        
        # Check title
        if not article.get('title'):
            issues.append("Missing title")
        elif len(article['title']) < 10:
            issues.append("Title too short")
        else:
            score += 20
        
        # Check content
        if not article.get('content'):
            issues.append("Missing content")
        elif len(article['content']) < 100:
            issues.append("Content too short")
        else:
            score += 30
        
        # Check for conflict keywords
        if article.get('is_conflict_related'):
            score += 25
        
        # Check for locations
        if article.get('detected_locations'):
            score += 15
        
        # Check for date
        if article.get('date_occurred'):
            score += 10
        
        return {
            'score': score,
            'issues': issues,
            'is_valid': score >= 50  # Minimum score threshold
        }

@celery_app.task(bind=True, name='app.tasks.data_processing_tasks.process_scraped_data')
def process_scraped_data(self, scraped_data: List[Dict[str, Any]]):
    """Process scraped articles to extract conflict events"""
    try:
        processor = DataProcessor()
        processed_events = []
        duplicates = []
        
        total_articles = len(scraped_data)
        
        # Update initial status
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': total_articles, 'status': 'Starting data processing'}
        )
        
        for i, article in enumerate(scraped_data):
            try:
                # Clean and validate article
                validation = processor.validate_article(article)
                if not validation['is_valid']:
                    logger.warning(f"Article failed validation: {validation['issues']}")
                    continue
                
                # Extract information
                cleaned_text = processor.clean_text(f"{article['title']} {article['content']}")
                
                event_data = {
                    'source': article['source'],
                    'source_url': article['url'],
                    'title': article['title'],
                    'content': article['content'],
                    'date_occurred': processor.extract_date(article['published_date']),
                    'event_type': processor.classify_event_type(cleaned_text),
                    'fatalities': processor.extract_fatalities(cleaned_text)[0],
                    'injured': processor.extract_fatalities(cleaned_text)[1],
                    'locations': processor.extract_locations(cleaned_text),
                    'actors': processor.extract_actors(cleaned_text),
                    'description': article['summary'] or article['title'],
                    'content_hash': processor.generate_content_hash(article),
                    'scraped_at': article['scraped_at'],
                    'processed_at': datetime.utcnow().isoformat()
                }
                
                # Check for duplicates
                if event_data['content_hash']:
                    # This would check against existing database records
                    pass
                
                processed_events.append(event_data)
                processor.processed_count += 1
                
                # Update progress
                if i % 10 == 0:
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'current': i + 1,
                            'total': total_articles,
                            'status': f'Processed {i + 1}/{total_articles} articles'
                        }
                    )
                
            except Exception as e:
                logger.error(f"Error processing article {i}: {str(e)}")
                processor.errors.append(str(e))
                continue
        
        # Update final status
        self.update_state(
            state='SUCCESS',
            meta={
                'current': total_articles,
                'total': total_articles,
                'status': 'Data processing completed',
                'processed_events': len(processed_events),
                'errors': len(processor.errors)
            }
        )
        
        logger.info(f"Data processing completed: {len(processed_events)} events processed, {len(processor.errors)} errors")
        
        return {
            'processed_at': datetime.utcnow().isoformat(),
            'total_articles': total_articles,
            'processed_events': len(processed_events),
            'duplicates_found': len(duplicates),
            'errors': processor.errors,
            'events': processed_events
        }
        
    except Exception as e:
        logger.error(f"Error in process_scraped_data task: {str(e)}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise

@celery_app.task(bind=True, name='app.tasks.data_processing_tasks.verify_conflict_data')
def verify_conflict_data(self, processed_events: List[Dict[str, Any]]):
    """Verify and cross-validate conflict data"""
    try:
        verified_events = []
        rejected_events = []
        
        total_events = len(processed_events)
        
        # Update initial status
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': total_events, 'status': 'Starting data verification'}
        )
        
        for i, event in enumerate(processed_events):
            try:
                # Verification criteria
                verification_score = 0
                
                # Check if event has required fields
                if event.get('date_occurred'):
                    verification_score += 25
                if event.get('locations'):
                    verification_score += 25
                if event.get('event_type') and event['event_type'] != 'unknown':
                    verification_score += 20
                if event.get('fatalities', 0) > 0 or event.get('injured', 0) > 0:
                    verification_score += 15
                if len(event.get('description', '')) > 50:
                    verification_score += 15
                
                # Cross-reference with other sources (simplified)
                # In production, this would check against other news outlets
                cross_ref_score = 0
                # cross_ref_score = cross_reference_with_other_sources(event)
                verification_score += cross_ref_score
                
                event['verification_score'] = verification_score
                event['is_verified'] = verification_score >= 60  # 60% threshold
                
                if event['is_verified']:
                    verified_events.append(event)
                else:
                    rejected_events.append(event)
                
                # Update progress
                if i % 10 == 0:
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'current': i + 1,
                            'total': total_events,
                            'status': f'Verified {i + 1}/{total_events} events'
                        }
                    )
                
            except Exception as e:
                logger.error(f"Error verifying event {i}: {str(e)}")
                rejected_events.append(event)
                continue
        
        # Update final status
        self.update_state(
            state='SUCCESS',
            meta={
                'current': total_events,
                'total': total_events,
                'status': 'Data verification completed',
                'verified_events': len(verified_events),
                'rejected_events': len(rejected_events)
            }
        )
        
        logger.info(f"Data verification completed: {len(verified_events)} verified, {len(rejected_events)} rejected")
        
        return {
            'verified_at': datetime.utcnow().isoformat(),
            'total_events': total_events,
            'verified_events': len(verified_events),
            'rejected_events': len(rejected_events),
            'verification_rate': (len(verified_events) / total_events * 100) if total_events > 0 else 0,
            'verified_data': verified_events
        }
        
    except Exception as e:
        logger.error(f"Error in verify_conflict_data task: {str(e)}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise

@celery_app.task(bind=True, name='app.tasks.data_processing_tasks.geocode_locations')
def geocode_locations(self, events: List[Dict[str, Any]]):
    """Geocode locations for conflict events"""
    try:
        processor = DataProcessor()
        geocoded_events = []
        
        total_events = len(events)
        
        # Update initial status
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': total_events, 'status': 'Starting geocoding'}
        )
        
        for i, event in enumerate(events):
            try:
                geocoded_locations = []
                
                for location in event.get('locations', []):
                    geocoded = processor.geocode_location(location)
                    if geocoded:
                        geocoded_locations.append(geocoded)
                
                event['geocoded_locations'] = geocoded_locations
                geocoded_events.append(event)
                
                # Update progress
                if i % 5 == 0:
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'current': i + 1,
                            'total': total_events,
                            'status': f'Geocoded {i + 1}/{total_events} events'
                        }
                    )
                
            except Exception as e:
                logger.error(f"Error geocoding event {i}: {str(e)}")
                continue
        
        # Update final status
        self.update_state(
            state='SUCCESS',
            meta={
                'current': total_events,
                'total': total_events,
                'status': 'Geocoding completed',
                'geocoded_events': len(geocoded_events)
            }
        )
        
        return {
            'geocoded_at': datetime.utcnow().isoformat(),
            'total_events': total_events,
            'geocoded_events': len(geocoded_events),
            'events': geocoded_events
        }
        
    except Exception as e:
        logger.error(f"Error in geocode_locations task: {str(e)}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise

@celery_app.task(bind=True, name='app.tasks.data_processing_tasks.store_conflict_data')
def store_conflict_data(self, verified_events: List[Dict[str, Any]]):
    """Store verified conflict data in database"""
    try:
        db = next(get_db())
        stored_events = []
        
        total_events = len(verified_events)
        
        # Update initial status
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': total_events, 'status': 'Starting data storage'}
        )
        
        for i, event_data in enumerate(verified_events):
            try:
                # Create or find location
                if event_data.get('geocoded_locations'):
                    primary_location = event_data['geocoded_locations'][0]
                    
                    # Check if location already exists
                    existing_location = db.query(Location).filter(
                        Location.name == primary_location['name']
                    ).first()
                    
                    if not existing_location:
                        location = Location(
                            name=primary_location['name'],
                            state=extract_state_from_location(primary_location['name']),
                            coordinates=f"POINT({primary_location['longitude']} {primary_location['latitude']})",
                            population_estimate=50000,  # Default estimate
                            created_at=datetime.utcnow()
                        )
                        db.add(location)
                        db.flush()
                        location_id = location.id
                    else:
                        location_id = existing_location.id
                
                # Create conflict event
                conflict = Conflict(
                    event_type=event_data['event_type'],
                    fatalities=event_data.get('fatalities', 0),
                    date_occurred=datetime.fromisoformat(event_data['date_occurred']),
                    location_id=location_id,
                    description=event_data['description'],
                    source=event_data['source'],
                    source_url=event_data['source_url'],
                    verification_score=event_data.get('verification_score', 0),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db.add(conflict)
                db.commit()
                stored_events.append(conflict.id)
                
                # Update progress
                if i % 5 == 0:
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'current': i + 1,
                            'total': total_events,
                            'status': f'Stored {i + 1}/{total_events} events'
                        }
                    )
                
            except Exception as e:
                logger.error(f"Error storing event {i}: {str(e)}")
                db.rollback()
                continue
        
        # Update final status
        self.update_state(
            state='SUCCESS',
            meta={
                'current': total_events,
                'total': total_events,
                'status': 'Data storage completed',
                'stored_events': len(stored_events)
            }
        )
        
        logger.info(f"Data storage completed: {len(stored_events)} events stored")
        
        return {
            'stored_at': datetime.utcnow().isoformat(),
            'total_events': total_events,
            'stored_events': len(stored_events),
            'event_ids': stored_events
        }
        
    except Exception as e:
        logger.error(f"Error in store_conflict_data task: {str(e)}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise
    finally:
        db.close()

def extract_state_from_location(location_name: str) -> str:
    """Extract state name from location"""
    location_lower = location_name.lower()
    
    for state in NIGERIAN_STATES.keys():
        if state in location_lower:
            return state.title()
    
    return 'Unknown'
