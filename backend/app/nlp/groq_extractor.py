"""
Groq Llama 3 NLP Event Extraction Engine
ACLED-level professional standard for conflict event extraction
"""

import os
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
from groq import Groq
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

class ExtractedEvent(BaseModel):
    """Structured schema for extracted conflict events"""
    incident_date: str = Field(..., description="YYYY-MM-DD format")
    location: Dict[str, str] = Field(default={"state": "Unknown", "lga": "Unknown", "community": "Unknown"}, description="Location with state, lga, community")
    crisis_type: str = Field(..., description="Crisis archetype from Nextier taxonomy")
    actor_primary: str = Field(..., description="Primary actor archetype")
    actor_secondary: Optional[str] = Field(None, description="Secondary actor archetype")
    fatalities: Optional[int] = Field(default=0, ge=0, description="Number of fatalities")
    injuries: Optional[int] = Field(None, ge=0, description="Number of injuries")
    source_url: str = Field(..., description="Source news article URL")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence")
    raw_text: str = Field(..., description="Original news article text")
    
    @validator('incident_date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

class GroqEventExtractor:
    """High-speed event extraction using Groq Llama 3"""
    
    MODEL_NAME = "llama-3.3-70b-versatile"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=self.api_key)
        self.model = self.MODEL_NAME
        logger.info(f"Initialized with model: {self.MODEL_NAME}")
        
        # Crisis archetypes from Nextier dataset
        self.crisis_archetypes = {
            'banditry': ['bandit', 'robbery', 'cattle rustling', 'kidnap for ransom'],
            'kidnapping': ['kidnap', 'abduction', 'hostage', 'ransom'],
            'gunmen attacks': ['gunmen', 'unknown gunmen', 'attack', 'shooting'],
            'cult clashes': ['cult', 'clash', 'rivalry', 'gang'],
            'extra-judicial killings': ['extra-judicial', 'killing', 'execution', 'summary'],
            'communal clash': ['communal', 'ethnic', 'religious', 'clash'],
            'terrorism': ['terrorism', 'boko haram', 'iswap', 'bomb', 'explosion'],
            'farmer-herder conflict': ['farmer', 'herder', 'grazing', 'crop'],
            'civil unrest': ['protest', 'riot', 'demonstration', 'unrest']
        }
        
        # Actor archetypes from Nextier dataset
        self.actor_archetypes = {
            'bandits': ['bandit', 'armed bandit', 'criminal'],
            'armed robber(s)': ['robber', 'armed robbery', 'thief'],
            'assassins': ['assassin', 'targeted killing'],
            'hoodlums': ['hoodlum', 'thug', 'miscreant'],
            'gunmen': ['gunmen', 'unknown gunmen', 'armed men'],
            'cultists': ['cultist', 'cult member'],
            'kidnappers': ['kidnapper', 'abductor'],
            'ISWAP': ['iswap', 'islamic state'],
            'Boko Haram': ['boko haram', 'jihadist', 'insurgent'],
            'Security Forces': ['police', 'army', 'military', 'security']
        }
        
        # Fatality quantization - Nextier "Vague Amounts" standard
        self.fatality_quantization = {
            'a couple': 2,
            'a few': 3,
            'several': 3,
            'tens': 11,
            'a dozen': 12,
            'more than a dozen': 13,
            'dozens': 24,
            'scores': 20,
            'hundreds': 100,
            'many': 5,  # Conservative estimate
            'numerous': 10,  # Conservative estimate
            'multiple': 3
        }

    def extract_event(self, article_text: str, source_url: str) -> Optional[ExtractedEvent]:
        """Extract structured event from article text using Groq Llama 3"""
        try:
            # Create the extraction prompt
            prompt = f"""
            Extract conflict event information from this Nigerian news article. Return valid JSON only.
            
            IMPORTANT: Always provide values for ALL fields. Use "Unknown" for missing text and 0 for numbers.
            
            Article: {article_text}
            
            Extract:
            - incident_date: Date in YYYY-MM-DD format (use today's date if not specified)
            - location: Object with state, lga, community (use "Unknown" if not mentioned)
            - crisis_type: One of {list(self.crisis_archetypes.keys())}
            - actor_primary: One of {list(self.actor_archetypes.keys())}
            - actor_secondary: One of {list(self.actor_archetypes.keys())} or null
            - fatalities: Integer number (use 0 if not mentioned)
            - injuries: Integer number or null
            
            CRITICAL: Never return null for state, lga, community, or fatalities. Always provide valid values.
            """
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert analyst specializing in conflict event extraction from Nigerian news articles.

Your task is to extract structured information about security incidents, conflicts, and violent events.

For each event, extract:
- event_type: Type of incident (e.g., "kidnapping", "bandit attack", "communal clash", "terrorism")
- location: Specific location(s) where the event occurred (state, LGA, town/village)
- date: Date of the event (extract from article or use publication date)
- actors: Groups or individuals involved (e.g., "bandits", "Boko Haram", "herders", "farmers")
- casualties: Number of deaths, injuries, or kidnappings (if mentioned)
- description: Brief  1-2 sentence summary of the event
- severity: "low", "medium", or "high" based on casualties and impact

Only extract events that involve:
- Violence or threats of violence
- Security incidents
- Conflicts between groups
- Terrorist activities
- Kidnappings or abductions
- Communal clashes

Do NOT extract:
- Political news without violence
- Economic stories
- General crime without conflict context
- Opinion pieces

Return your response as a JSON object with an "events" array."""
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.2,  # Low temperature for factual extraction
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            extracted_data = json.loads(response.choices[0].message.content)
            
            # Process and validate the extracted data
            processed_event = self._process_extracted_data(extracted_data, article_text, source_url)
            
            return processed_event
            
        except Exception as e:
            logger.error(f"Error extracting event: {str(e)}")
            return None

    def _create_extraction_prompt(self, article_text: str, source_url: str) -> str:
        """Create structured prompt for event extraction"""
        
        crisis_types = list(self.crisis_archetypes.keys())
        actor_types = list(self.actor_archetypes.keys())
        
        prompt = f"""
Extract conflict event details from this Nigerian news article. Return ONLY valid JSON with these exact fields:

{{
    "incident_date": "YYYY-MM-DD (extract from article or use publication date)",
    "location": {{
        "state": "Nigerian state name",
        "lga": "Local Government Area name", 
        "community": "Community/Town name"
    }},
    "crisis_type": "One of: {', '.join(crisis_types)}",
    "actor_primary": "One of: {', '.join(actor_types)}",
    "actor_secondary": "Optional: One of: {', '.join(actor_types)} or null",
    "fatalities": "Number (exact if specified, otherwise estimate from vague terms)",
    "injuries": "Number or null if not mentioned",
    "confidence_score": "0.0-1.0 based on information clarity"
}}

CRISIS TYPE MAPPING:
- Banditry: Armed robbery, cattle rustling, kidnapping for ransom
- Kidnapping: Abduction, hostage situations
- Gunmen Attacks: Attacks by unknown armed men
- Cult Clashes: Violence between cult groups
- Extra-Judicial Killings: Killings without due process
- Communal Clash: Ethnic/religious community violence
- Terrorism: Boko Haram, ISWAP, bomb attacks
- Farmer-Herder Conflict: Disputes between farmers and herders
- Civil Unrest: Protests, riots, demonstrations

ACTOR MAPPING:
- Bandits: Criminal armed groups
- Armed Robber(s): Theft perpetrators
- Assassins: Targeted killers
- Hoodlums: Criminal elements
- Gunmen: Unknown armed attackers
- Cultists: Cult group members
- Kidnappers: Abduction perpetrators
- ISWAP: Islamic State affiliates
- Boko Haram: Jihadist insurgents
- Security Forces: Police, military, etc.

FATALITY CONVERSION:
- "A couple" = 2
- "A few/Several" = 3
- "Tens" = 11
- "A dozen" = 12
- "More than a dozen" = 13
- "Scores" = 20
- "Dozens" = 24
- "Hundreds" = 100

ARTICLE TEXT:
{article_text}

SOURCE URL: {source_url}

Return ONLY the JSON object, no explanations.
"""
        return prompt

    def _process_extracted_data(self, data: dict, raw_text: str, source_url: str) -> ExtractedEvent:
        """Process and validate extracted data"""
        
        # Handle null values in location
        location = data.get('location', {})
        if location is None:
            location = {}
        
        data['location'] = {
            'state': location.get('state') or 'Unknown',
            'lga': location.get('lga') or 'Unknown',
            'community': location.get('community') or 'Unknown'
        }
        
        # Handle null fatalities
        if data.get('fatalities') is None:
            data['fatalities'] = 0
        elif isinstance(data['fatalities'], str):
            data['fatalities'] = self._quantize_fatalities(data['fatalities'])
        
        # Handle null values for required fields
        data['incident_date'] = data.get('incident_date') or datetime.now().strftime('%Y-%m-%d')
        data['crisis_type'] = data.get('crisis_type') or 'Unknown'
        data['actor_primary'] = data.get('actor_primary') or 'Unknown'
        
        # Validate crisis type
        if data['crisis_type'] not in self.crisis_archetypes:
            # Find closest match based on keywords
            data['crisis_type'] = self._find_crisis_type(raw_text)
        
        # Validate actor types
        if data['actor_primary'] not in self.actor_archetypes:
            data['actor_primary'] = self._find_actor_type(raw_text)
        
        if data.get('actor_secondary') and data['actor_secondary'] not in self.actor_archetypes:
            data['actor_secondary'] = None
        
        # Add required fields
        data['source_url'] = source_url
        data['raw_text'] = raw_text
        
        # Calculate confidence score if not provided
        if 'confidence_score' not in data:
            data['confidence_score'] = self._calculate_confidence_score(data, raw_text)
        
        return ExtractedEvent(**data)

    def _quantize_fatalities(self, fatality_text: str) -> int:
        """Convert vague fatality descriptions to numbers"""
        fatality_text = fatality_text.lower().strip()
        
        # Check for exact numbers first
        number_match = re.search(r'\d+', fatality_text)
        if number_match:
            return int(number_match.group())
        
        # Check for vague terms
        for vague_term, number in self.fatality_quantization.items():
            if vague_term in fatality_text:
                return number
        
        # Default to 1 if fatalities mentioned but no quantity
        if 'fatalit' in fatality_text or 'killed' in fatality_text or 'dead' in fatality_text:
            return 1
        
        return 0

    def _find_crisis_type(self, text: str) -> str:
        """Find crisis type based on keywords in text"""
        text_lower = text.lower()
        
        for crisis_type, keywords in self.crisis_archetypes.items():
            if any(keyword in text_lower for keyword in keywords):
                return crisis_type
        
        return 'civil unrest'  # Default fallback

    def _find_actor_type(self, text: str) -> str:
        """Find actor type based on keywords in text"""
        text_lower = text.lower()
        
        for actor_type, keywords in self.actor_archetypes.items():
            if any(keyword in text_lower for keyword in keywords):
                return actor_type
        
        return 'gunmen'  # Default fallback for unknown armed actors

    def _calculate_confidence_score(self, data: Dict[str, Any], raw_text: str) -> float:
        """Calculate confidence score based on extracted data quality"""
        score = 0.0
        
        # Check if essential fields are present
        if data.get('crisis_type') and data.get('crisis_type') != 'Unknown':
            score += 0.3
        if data.get('actor_primary') and data.get('actor_primary') != 'Unknown':
            score += 0.3
        if data.get('location') and data.get('location', {}).get('state') != 'Unknown':
            score += 0.2
        # Actor identification (15 points)
        if data.get('actor_primary') and data['actor_primary'] != 'unknown':
            score += 0.1
        if data.get('actor_secondary'):
            score += 0.05
        
        # Fatality information (10 points)
        if data.get('fatalities', 0) > 0:
            score += 0.1
        
        # Text length and detail (10 points)
        if len(text) > 500:
            score += 0.05
        if len(text) > 1000:
            score += 0.05
        
        return min(score, 1.0)
    
    def batch_extract(self, articles: List[Dict[str, str]]) -> Dict:
        """
        Extract events from multiple articles.
        
        Returns:
            Dictionary with 'events' and 'stats'
        """
        all_events = []
        stats = {
            'total_articles': len(articles),
            'articles_processed': 0,
            'articles_with_events': 0,
            'total_events_extracted': 0,
            'failed_articles': 0
        }
        
        for idx, article in enumerate(articles, 1):
            logger.info(f"Processing article {idx}/{len(articles)}")
            
            # Extract event from article
            event = self.extract_event(
                article.get('content', article.get('summary', '')),
                article.get('url', '')
            )
            
            if event:
                all_events.append(event)
                stats['articles_with_events'] += 1
                stats['total_events_extracted'] += 1
                stats['articles_processed'] += 1
            else:
                # Article processed but no events found or failed
                stats['articles_processed'] += 1
                if not article.get('content'):
                    stats['failed_articles'] += 1
        
        # Calculate success rate
        if stats['articles_processed'] > 0:
            stats['extraction_rate'] = f"{(stats['articles_with_events'] / stats['articles_processed'] * 100):.1f}%"
        else:
            stats['extraction_rate'] = "0.0%"
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Extraction Summary:")
        logger.info(f"  Articles processed: {stats['articles_processed']}/{stats['total_articles']}")
        logger.info(f"  Events extracted: {stats['total_events_extracted']}")
        logger.info(f"  Extraction rate: {stats['extraction_rate']}")
        logger.info(f"{'='*60}")
        
        return {
            'events': all_events,
            'stats': stats,
            'extracted_at': datetime.utcnow().isoformat()
        }

# Example usage
if __name__ == "__main__":
    extractor = GroqEventExtractor()
    
    sample_text = """
    Unknown gunmen attacked a farming community in Bokkos Local Government Area of Plateau State on Monday, 
    killing at least 12 people and injuring several others. The attackers stormed the village at night, 
    setting houses on fire and shooting indiscriminately. Security forces have been deployed to the area.
    """
    
    event = extractor.extract_event(sample_text, "https://example.com/news-article")
    if event:
        print(json.dumps(event.dict(), indent=2))
