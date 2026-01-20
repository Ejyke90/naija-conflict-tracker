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
    location: Dict[str, str] = Field(..., description="Location with state, lga, community")
    crisis_type: str = Field(..., description="Crisis archetype from Nextier taxonomy")
    actor_primary: str = Field(..., description="Primary actor archetype")
    actor_secondary: Optional[str] = Field(None, description="Secondary actor archetype")
    fatalities: int = Field(..., ge=0, description="Number of fatalities")
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
    
    def __init__(self, api_key: str = None):
        self.client = Groq(api_key=api_key or os.getenv('GROQ_API_KEY'))
        self.model = "llama3-70b-8192"
        
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
        """Extract structured event from news article text"""
        try:
            # Create the extraction prompt
            prompt = self._create_extraction_prompt(article_text, source_url)
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert conflict event extractor for Nigeria. Extract structured data from news articles and return ONLY valid JSON. Be precise and factual."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=1000,
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

    def _process_extracted_data(self, data: Dict[str, Any], raw_text: str, source_url: str) -> ExtractedEvent:
        """Process and validate extracted data"""
        
        # Quantize fatalities if vague terms used
        if isinstance(data.get('fatalities'), str):
            data['fatalities'] = self._quantize_fatalities(data['fatalities'])
        
        # Validate crisis type
        if data.get('crisis_type') not in self.crisis_archetypes:
            # Find closest match based on keywords
            data['crisis_type'] = self._find_crisis_type(raw_text)
        
        # Validate actor types
        if data.get('actor_primary') not in self.actor_archetypes:
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

    def _calculate_confidence_score(self, data: Dict[str, Any], text: str) -> float:
        """Calculate confidence score based on information completeness"""
        score = 0.0
        
        # Date extraction (20 points)
        if data.get('incident_date') and data['incident_date'] != 'unknown':
            score += 0.2
        
        # Location information (25 points)
        location = data.get('location', {})
        if location.get('state'):
            score += 0.1
        if location.get('lga'):
            score += 0.1
        if location.get('community'):
            score += 0.05
        
        # Crisis type identification (20 points)
        if data.get('crisis_type') and data['crisis_type'] != 'unknown':
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
