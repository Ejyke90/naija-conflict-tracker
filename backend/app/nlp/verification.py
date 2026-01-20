"""
Confidence Scoring and Verification System
Validates extracted events and determines publication status
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlparse
from app.nlp.groq_extractor import ExtractedEvent
from app.nlp.geocoding import NigerianGeocoder

logger = logging.getLogger(__name__)

class EventVerificationSystem:
    """Verifies extracted events and assigns confidence scores"""
    
    def __init__(self, geocoder: NigerianGeocoder = None):
        self.geocoder = geocoder or NigerianGeocoder()
        
        # Confidence thresholds
        self.AUTO_PUBLISH_THRESHOLD = 0.85
        self.MINIMUM_THRESHOLD = 0.60
        self.PENDING_VERIFICATION_THRESHOLD = 0.70
        
        # Source quality weights
        self.source_weights = {
            'channels_tv': 0.95,      # Highest quality, reliable
            'daily_trust': 0.90,      # Excellent northern coverage
            'punch': 0.88,            # Good national coverage
            'vanguard': 0.85,         # Reliable reporting
            'daily_nigerian': 0.80    # Good but newer source
        }
        
        # Crisis type reliability weights
        self.crisis_reliability = {
            'terrorism': 0.95,        # Usually well-reported
            'kidnapping': 0.90,       # Clear events
            'farmer-herder conflict': 0.85,
            'communal clash': 0.85,
            'banditry': 0.80,         # Sometimes underreported
            'gunmen attacks': 0.75,   # Can be vague
            'cult clashes': 0.75,
            'extra-judicial killings': 0.70,
            'civil unrest': 0.65      # Can be exaggerated
        }
        
        # Actor reliability weights
        self.actor_reliability = {
            'Security Forces': 0.95,     # Official sources
            'Boko Haram': 0.95,          # Clear attribution
            'ISWAP': 0.95,
            'bandits': 0.85,             # Generally accurate
            'kidnappers': 0.85,
            'gunmen': 0.75,              # Often unknown
            'cultists': 0.75,
            'armed robber(s)': 0.70,
            'assassins': 0.70,
            'hoodlums': 0.65
        }

    def verify_event(self, event: ExtractedEvent) -> Dict[str, Any]:
        """
        Verify an extracted event and determine publication status
        
        Args:
            event: Extracted event from NLP pipeline
            
        Returns:
            Verification result with status and confidence score
        """
        try:
            # Calculate comprehensive confidence score
            confidence_scores = self._calculate_confidence_components(event)
            final_score = self._calculate_final_score(confidence_scores)
            
            # Determine verification status
            status = self._determine_status(final_score, confidence_scores)
            
            # Create verification result
            result = {
                'event_id': self._generate_event_id(event),
                'verification_status': status,
                'confidence_score': final_score,
                'confidence_components': confidence_scores,
                'verified_at': datetime.utcnow().isoformat(),
                'requires_human_review': status in ['pending_verification', 'low_confidence'],
                'reasoning': self._generate_reasoning(confidence_scores, status),
                'recommendations': self._generate_recommendations(confidence_scores)
            }
            
            # Add geocoding verification
            geo_verification = self._verify_geocoding(event)
            result['geocoding_verification'] = geo_verification
            
            # Add cross-reference checks
            cross_reference = self._cross_reference_check(event)
            result['cross_reference'] = cross_reference
            
            return result
            
        except Exception as e:
            logger.error(f"Error verifying event: {str(e)}")
            return {
                'verification_status': 'error',
                'confidence_score': 0.0,
                'error': str(e)
            }

    def _calculate_confidence_components(self, event: ExtractedEvent) -> Dict[str, float]:
        """Calculate individual confidence components"""
        components = {}
        
        # Source reliability (20%)
        source_key = self._extract_source_from_url(event.source_url)
        source_weight = self.source_weights.get(source_key, 0.70)
        components['source_reliability'] = source_weight * 0.20
        
        # Date specificity (15%)
        date_score = self._score_date_specificity(event.incident_date)
        components['date_specificity'] = date_score * 0.15
        
        # Location precision (20%)
        location_score = self._score_location_precision(event.location)
        components['location_precision'] = location_score * 0.20
        
        # Crisis type clarity (15%)
        crisis_score = self.crisis_reliability.get(event.crisis_type, 0.70)
        components['crisis_type_clarity'] = crisis_score * 0.15
        
        # Actor identification (15%)
        actor_score = self._score_actor_identification(event)
        components['actor_identification'] = actor_score * 0.15
        
        # Fatality specificity (10%)
        fatality_score = self._score_fatality_specificity(event.fatalities, event.raw_text)
        components['fatality_specificity'] = fatality_score * 0.10
        
        # Text quality and detail (5%)
        text_score = self._score_text_quality(event.raw_text)
        components['text_quality'] = text_score * 0.05
        
        return components

    def _calculate_final_score(self, components: Dict[str, float]) -> float:
        """Calculate final confidence score from components"""
        return sum(components.values())

    def _determine_status(self, final_score: float, components: Dict[str, float]) -> str:
        """Determine verification status based on scores"""
        
        # Check for critical failures
        if components['location_precision'] < 0.10:
            return 'location_missing'
        
        if components['date_specificity'] < 0.05:
            return 'date_missing'
        
        if final_score >= self.AUTO_PUBLISH_THRESHOLD:
            return 'auto_publish'
        elif final_score >= self.PENDING_VERIFICATION_THRESHOLD:
            return 'pending_verification'
        elif final_score >= self.MINIMUM_THRESHOLD:
            return 'low_confidence'
        else:
            return 'reject'

    def _score_date_specificity(self, date_str: str) -> float:
        """Score date specificity"""
        if not date_str or date_str == 'unknown':
            return 0.0
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Recent dates get higher scores
            days_ago = (datetime.utcnow() - date).days
            
            if days_ago <= 1:
                return 1.0
            elif days_ago <= 7:
                return 0.9
            elif days_ago <= 30:
                return 0.8
            else:
                return 0.6
                
        except ValueError:
            return 0.0

    def _score_location_precision(self, location: Dict[str, str]) -> float:
        """Score location precision"""
        score = 0.0
        
        if location.get('community') and location['community'] != 'Unknown':
            score += 0.5
        if location.get('lga') and location['lga'] != 'Unknown':
            score += 0.3
        if location.get('state') and location['state'] != 'Unknown':
            score += 0.2
        
        # Validate location exists
        if self.geocoder.validate_location(location.get('state', ''), location.get('lga')):
            score += 0.1
        
        return min(score, 1.0)

    def _score_actor_identification(self, event: ExtractedEvent) -> float:
        """Score actor identification"""
        score = 0.0
        
        # Primary actor
        primary_reliability = self.actor_reliability.get(event.actor_primary, 0.70)
        score += primary_reliability * 0.7
        
        # Secondary actor adds confidence
        if event.actor_secondary:
            secondary_reliability = self.actor_reliability.get(event.actor_secondary, 0.70)
            score += secondary_reliability * 0.3
        
        return min(score, 1.0)

    def _score_fatality_specificity(self, fatalities: int, raw_text: str) -> float:
        """Score fatality reporting specificity"""
        if fatalities == 0:
            return 0.3  # Low confidence when no fatalities mentioned
        
        # Check for exact numbers vs vague terms
        if 'killed' in raw_text.lower() or 'dead' in raw_text.lower():
            if str(fatalities) in raw_text:
                return 1.0  # Exact number mentioned
            else:
                return 0.8  # Fatalities mentioned but no specific number
        
        # Vague terms
        vague_terms = ['several', 'few', 'many', 'some']
        if any(term in raw_text.lower() for term in vague_terms):
            return 0.6
        
        return 0.7

    def _score_text_quality(self, raw_text: str) -> float:
        """Score text quality and detail"""
        if not raw_text:
            return 0.0
        
        score = 0.0
        
        # Length indicates detail
        length = len(raw_text)
        if length > 1000:
            score += 0.4
        elif length > 500:
            score += 0.3
        elif length > 200:
            score += 0.2
        else:
            score += 0.1
        
        # Presence of quotes indicates quality reporting
        if '"' in raw_text or "'" in raw_text:
            score += 0.2
        
        # Official sources mentioned
        official_terms = ['police', 'army', 'military', 'security', 'spokesperson', 'official']
        if any(term in raw_text.lower() for term in official_terms):
            score += 0.2
        
        # Specific details (times, places, numbers)
        import re
        if re.search(r'\d+:\d+', raw_text):  # Time mentioned
            score += 0.1
        if re.search(r'\d+(km|kilometers?|miles?)', raw_text):  # Distance mentioned
            score += 0.1
        
        return min(score, 1.0)

    def _verify_geocoding(self, event: ExtractedEvent) -> Dict[str, Any]:
        """Verify geocoding results"""
        try:
            geo_result = self.geocoder.geocode_location(event.location)
            
            if not geo_result:
                return {
                    'status': 'failed',
                    'reason': 'Location not found in database'
                }
            
            return {
                'status': 'success',
                'precision': geo_result['precision'],
                'coordinates': {
                    'latitude': geo_result['latitude'],
                    'longitude': geo_result['longitude']
                },
                'confidence': 1.0 if geo_result['precision'] == 'community' else 0.8
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def _cross_reference_check(self, event: ExtractedEvent) -> Dict[str, Any]:
        """Check for cross-references with other events"""
        # This would implement database cross-referencing
        # For now, return placeholder
        return {
            'similar_events_found': 0,
            'potential_duplicates': [],
            'cross_reference_score': 0.0
        }

    def _generate_event_id(self, event: ExtractedEvent) -> str:
        """Generate unique event ID"""
        import hashlib
        content = f"{event.incident_date}{event.location['state']}{event.crisis_type}{event.fatalities}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _extract_source_from_url(self, url: str) -> str:
        """Extract source key from URL"""
        domain = urlparse(url).netloc.lower()
        
        if 'punchng.com' in domain:
            return 'punch'
        elif 'channelstv.com' in domain:
            return 'channels_tv'
        elif 'dailynigerian.com' in domain:
            return 'daily_nigerian'
        elif 'vanguardngr.com' in domain:
            return 'vanguard'
        elif 'dailytrust.com.ng' in domain:
            return 'daily_trust'
        else:
            return 'unknown'

    def _generate_reasoning(self, components: Dict[str, float], status: str) -> str:
        """Generate human-readable reasoning for verification status"""
        reasoning_parts = []
        
        if components['source_reliability'] > 0.15:
            reasoning_parts.append("Reliable source")
        if components['location_precision'] > 0.15:
            reasoning_parts.append("Precise location")
        if components['date_specificity'] > 0.10:
            reasoning_parts.append("Specific date")
        if components['crisis_type_clarity'] > 0.10:
            reasoning_parts.append("Clear event type")
        if components['actor_identification'] > 0.10:
            reasoning_parts.append("Identified actors")
        if components['fatality_specificity'] > 0.05:
            reasoning_parts.append("Specific casualty count")
        
        if status == 'auto_publish':
            return "High confidence: " + ", ".join(reasoning_parts)
        elif status == 'pending_verification':
            return "Moderate confidence: " + ", ".join(reasoning_parts) + " - Requires review"
        elif status == 'low_confidence':
            return "Low confidence: Limited information - Verification recommended"
        else:
            return "Rejected: Insufficient reliable information"

    def _generate_recommendations(self, components: Dict[str, float]) -> List[str]:
        """Generate recommendations for improving event quality"""
        recommendations = []
        
        if components['source_reliability'] < 0.15:
            recommendations.append("Seek additional sources for confirmation")
        
        if components['location_precision'] < 0.30:
            recommendations.append("Verify location details - consider manual geocoding")
        
        if components['date_specificity'] < 0.10:
            recommendations.append("Confirm incident date with additional sources")
        
        if components['actor_identification'] < 0.10:
            recommendations.append("Actor identification unclear - seek more details")
        
        if components['fatality_specificity'] < 0.05:
            recommendations.append("Casualty figures need verification")
        
        if not recommendations:
            recommendations.append("Event appears well-documented")
        
        return recommendations

    def batch_verify_events(self, events: List[ExtractedEvent]) -> List[Dict[str, Any]]:
        """Verify multiple events in batch"""
        results = []
        
        for event in events:
            result = self.verify_event(event)
            results.append(result)
        
        # Generate batch summary
        summary = {
            'total_events': len(events),
            'auto_publish': sum(1 for r in results if r['verification_status'] == 'auto_publish'),
            'pending_verification': sum(1 for r in results if r['verification_status'] == 'pending_verification'),
            'low_confidence': sum(1 for r in results if r['verification_status'] == 'low_confidence'),
            'rejected': sum(1 for r in results if r['verification_status'] in ['reject', 'location_missing', 'date_missing']),
            'average_confidence': sum(r['confidence_score'] for r in results) / len(results) if results else 0
        }
        
        return {
            'events': results,
            'summary': summary,
            'processed_at': datetime.utcnow().isoformat()
        }

# Example usage
if __name__ == "__main__":
    from app.nlp.groq_extractor import ExtractedEvent
    
    verifier = EventVerificationSystem()
    
    # Sample event
    sample_event = ExtractedEvent(
        incident_date="2024-01-15",
        location={"state": "Plateau", "lga": "Bokkos", "community": "Mushere"},
        crisis_type="Farmer-Herder Conflict",
        actor_primary="Herder(s)",
        actor_secondary="Farmer(s)",
        fatalities=12,
        source_url="https://punchng.com/conflict-article",
        confidence_score=0.0,
        raw_text="Unknown gunmen attacked a farming community..."
    )
    
    result = verifier.verify_event(sample_event)
    print(f"Status: {result['verification_status']}")
    print(f"Confidence: {result['confidence_score']}")
    print(f"Reasoning: {result['reasoning']}")
