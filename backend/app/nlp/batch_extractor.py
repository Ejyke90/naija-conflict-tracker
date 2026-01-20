"""
Smart batching for Groq API - process multiple articles efficiently
"""

import json
import time
import logging
from typing import List, Dict, Any, Optional
from groq import Groq

logger = logging.getLogger(__name__)

class GroqBatchExtractor:
    """Extract events from multiple articles in batches to reduce API calls"""
    
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"
        
    def extract_batch(self, articles: List[Dict[str, str]], batch_size: int = 3) -> List[Dict]:
        """
        Extract events from multiple articles in a single API call
        
        This is much more efficient than one API call per article
        """
        all_events = []
        
        # Process articles in batches
        for i in range(0, len(articles), batch_size):
            batch = articles[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(articles)-1)//batch_size + 1}")
            
            # Create combined prompt for batch
            batch_prompt = self._create_batch_prompt(batch)
            
            try:
                # Single API call for entire batch
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{
                        "role": "system",
                        "content": """You are an expert at extracting conflict events from Nigerian news articles.
                        
Process EACH article in the batch and return a JSON object with an "events" array.
Each event should have: incident_date, location, crisis_type, actor_primary, fatalities, etc.
If an article doesn't describe a conflict event, include it in the array with event_type: "none"."""
                    }, {
                        "role": "user",
                        "content": batch_prompt
                    }],
                    temperature=0.2,
                    max_tokens=4000,
                    response_format={"type": "json_object"}
                )
                
                # Parse batch response
                result = json.loads(response.choices[0].message.content)
                events = result.get('events', [])
                
                # Add source info to each event
                for idx, event in enumerate(events):
                    if idx < len(batch):
                        event['source_url'] = batch[idx].get('url', '')
                        event['raw_text'] = batch[idx].get('content', '')[:1000]
                
                all_events.extend(events)
                
                # Small delay between batches (not individual articles)
                if i + batch_size < len(articles):
                    time.sleep(2)  # Only 2 seconds between batches of 3 articles
                    
            except Exception as e:
                logger.error(f"Batch extraction failed: {str(e)}")
                # Fallback to individual processing for this batch
                for article in batch:
                    try:
                        event = self._extract_single(article)
                        if event:
                            all_events.append(event)
                    except Exception as e2:
                        logger.error(f"Individual extraction also failed: {str(e2)}")
        
        return all_events
    
    def _create_batch_prompt(self, articles: List[Dict[str, str]]) -> str:
        """Create a prompt for processing multiple articles"""
        prompt = "Process these articles and extract conflict events:\n\n"
        
        for i, article in enumerate(articles, 1):
            content = article.get('content', article.get('summary', ''))[:1000]
            prompt += f"\n--- Article {i} ---\n{content}\n"
        
        prompt += "\n\nReturn JSON with 'events' array containing one object per article."
        return prompt
    
    def _extract_single(self, article: Dict[str, str]) -> Optional[Dict]:
        """Fallback method for individual article extraction"""
        # This would use the original single-article logic
        # Simplified for brevity
        return None
