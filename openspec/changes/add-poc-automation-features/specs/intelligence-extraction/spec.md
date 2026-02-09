# Intelligence Extraction Specification

## ADDED Requirements

### Requirement: LLM-Powered Event Extraction
The system SHALL automatically extract structured conflict event data from unstructured news article text using Large Language Models.

#### Scenario: Extract Event from News Article
- **GIVEN** a news article about a conflict in Nigeria
- **WHEN** the article is processed by the intelligence extraction service
- **THEN** the system SHALL extract:
  - Event location (state, LGA, locality)
  - Armed actors involved
  - Casualty count (deaths, injuries)
  - Conflict type classification
  - Event date
  - Severity score (1-10)
- **AND** SHALL return structured JSON data
- **AND** SHALL complete within 2 minutes

#### Scenario: Handle Ambiguous or Incomplete Information
- **GIVEN** an article with incomplete information
- **WHEN** extraction is attempted
- **THEN** the system SHALL mark missing fields as null
- **AND** SHALL provide confidence scores for each extracted field
- **AND** SHALL NOT fabricate information

#### Scenario: LLM Service Unavailable
- **GIVEN** the LLM service is down or unresponsive
- **WHEN** extraction is attempted
- **THEN** the system SHALL trigger circuit breaker after 5 failures
- **AND** SHALL fall back to rule-based extraction (if available)
- **AND** SHALL queue articles for retry when service recovers

### Requirement: Multi-Provider LLM Support
The system SHALL support both local (Ollama) and cloud (OpenAI) LLM providers with automatic fallback.

#### Scenario: Use Local Ollama for Development
- **GIVEN** `LLM_PROVIDER=ollama` is configured
- **WHEN** extraction is requested
- **THEN** the system SHALL use local Ollama instance
- **AND** SHALL use model `llama3.2:latest` by default
- **AND** SHALL NOT incur API costs

#### Scenario: Use OpenAI for Production
- **GIVEN** `LLM_PROVIDER=openai` is configured
- **AND** valid API key is provided
- **WHEN** extraction is requested
- **THEN** the system SHALL use OpenAI GPT-4
- **AND** SHALL track token usage
- **AND** SHALL respect rate limits

#### Scenario: Automatic Fallback
- **GIVEN** primary LLM provider fails
- **WHEN** extraction is attempted
- **THEN** the system SHALL try secondary provider
- **AND** SHALL log the fallback event
- **AND** SHALL continue processing without manual intervention

### Requirement: Intelligent Result Caching
The system SHALL cache LLM responses to avoid redundant API calls and reduce costs.

#### Scenario: Cache Hit on Duplicate Article
- **GIVEN** an article has been processed previously
- **WHEN** the same article content is submitted again
- **THEN** the system SHALL return cached extraction result
- **AND** SHALL NOT make a new LLM API call
- **AND** response time SHALL be <100ms

#### Scenario: Cache Expiration
- **GIVEN** cached results are older than 24 hours
- **WHEN** the article is processed again
- **THEN** the system SHALL make a fresh LLM call
- **AND** SHALL update the cache with new results

#### Scenario: Cache Key Generation
- **GIVEN** an article text
- **WHEN** generating cache key
- **THEN** the system SHALL use MD5 hash of normalized text
- **AND** SHALL include LLM provider and model version in key
- **AND** SHALL handle cache key collisions safely

### Requirement: Batch Processing for Efficiency
The system SHALL support batch processing of multiple articles to optimize LLM usage.

#### Scenario: Process Batch of 10 Articles
- **GIVEN** 10 articles are queued for extraction
- **WHEN** batch processing is triggered
- **THEN** the system SHALL process articles sequentially
- **AND** SHALL respect rate limits (1 request per second)
- **AND** SHALL continue processing even if one article fails
- **AND** SHALL return all results when batch completes

#### Scenario: Batch Timeout Handling
- **GIVEN** a batch of articles is being processed
- **WHEN** processing time exceeds 30 minutes
- **THEN** the system SHALL mark unprocessed articles as pending
- **AND** SHALL return successfully processed articles
- **AND** SHALL reschedule timeout articles for retry

### Requirement: Automated Conflict Categorization
The system SHALL classify conflict events into predefined archetypes with confidence scoring.

#### Scenario: Categorize Banditry Event
- **GIVEN** an article about armed bandits attacking a village
- **WHEN** categorization is performed
- **THEN** the system SHALL classify as "Banditry"
- **AND** SHALL provide confidence score (e.g., 92%)
- **AND** SHALL include reasoning for classification

#### Scenario: Handle Multiple Conflict Types
- **GIVEN** an article describing multiple conflict types
- **WHEN** categorization is performed
- **THEN** the system SHALL identify primary category
- **AND** SHALL list secondary categories if applicable
- **AND** SHALL weight confidence by context and location

#### Scenario: Low Confidence Categorization
- **GIVEN** an article with ambiguous conflict description
- **WHEN** categorization is performed
- **AND** confidence score is below 70%
- **THEN** the system SHALL flag for manual review
- **AND** SHALL assign category "Other" as placeholder
- **AND** SHALL log low-confidence cases for model improvement

### Requirement: Entity Recognition and Normalization
The system SHALL extract and normalize named entities from articles.

#### Scenario: Extract Nigerian Location Names
- **GIVEN** an article mentions "Kaduna State" and "Birnin Gwari LGA"
- **WHEN** entity extraction is performed
- **THEN** the system SHALL identify:
  - State: "Kaduna"
  - LGA: "Birnin Gwari"
- **AND** SHALL normalize to standard names in database
- **AND** SHALL link to geospatial coordinates

#### Scenario: Identify Armed Actor Groups
- **GIVEN** an article mentions "Boko Haram" or "bandits"
- **WHEN** entity extraction is performed
- **THEN** the system SHALL identify actor type
- **AND** SHALL normalize spelling variations
- **AND** SHALL map to standardized actor taxonomy

#### Scenario: Extract Casualty Figures
- **GIVEN** an article states "15 people killed and 23 injured"
- **WHEN** casualty extraction is performed
- **THEN** the system SHALL extract:
  - Deaths: 15
  - Injuries: 23
- **AND** SHALL handle variations ("15 dead", "fifteen killed")
- **AND** SHALL mark uncertain figures with confidence < 80%

### Requirement: Quality Assurance and Validation
The system SHALL validate extracted data for accuracy and completeness.

#### Scenario: Validate Extracted Location
- **GIVEN** an extracted location name
- **WHEN** validation is performed
- **THEN** the system SHALL verify location exists in Nigerian geography database
- **AND** SHALL reject invalid or foreign locations
- **AND** SHALL attempt spelling correction if close match found

#### Scenario: Validate Date Consistency
- **GIVEN** an extracted event date
- **WHEN** validation is performed
- **THEN** the system SHALL ensure date is not in the future
- **AND** SHALL check consistency with article publication date
- **AND** SHALL flag dates more than 1 month old as potentially historical

#### Scenario: Validate Casualty Numbers
- **GIVEN** extracted casualty figures
- **WHEN** validation is performed
- **THEN** the system SHALL check for reasonable ranges (0-10,000)
- **AND** SHALL flag outliers for review
- **AND** SHALL ensure deaths <= total casualties

## Configuration

### Environment Variables
```bash
# LLM Provider
LLM_PROVIDER=ollama  # or openai
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview

# Circuit Breaker
LLM_CIRCUIT_BREAKER_THRESHOLD=5
LLM_CIRCUIT_BREAKER_TIMEOUT=30

# Caching
LLM_CACHE_TTL=86400  # 24 hours
LLM_CACHE_ENABLED=true

# Batch Processing
LLM_BATCH_SIZE=10
LLM_RATE_LIMIT_PER_SECOND=1
LLM_TIMEOUT_SECONDS=120

# Categorization
CATEGORIZATION_CONFIDENCE_THRESHOLD=70
AUTO_CATEGORIZATION_ENABLED=true
```

### Database Schema
```sql
CREATE TABLE extracted_events (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id),
    event_location JSONB,  -- {state, lga, locality, coordinates}
    armed_actors TEXT[],
    casualties JSONB,  -- {deaths, injuries, missing}
    conflict_type VARCHAR(50),
    conflict_category VARCHAR(100),
    category_confidence FLOAT,
    severity_score INTEGER CHECK (severity_score BETWEEN 1 AND 10),
    event_date DATE,
    extraction_metadata JSONB,  -- {llm_provider, model, processing_time}
    validated BOOLEAN DEFAULT false,
    requires_review BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_extracted_events_conflict_type ON extracted_events(conflict_type);
CREATE INDEX idx_extracted_events_category ON extracted_events(conflict_category);
CREATE INDEX idx_extracted_events_event_date ON extracted_events(event_date DESC);
```

### Conflict Archetype Taxonomy
```
- Banditry
- Kidnapping
- Farmer-Herder Clashes
- Gunmen Violence
- Cult Violence
- Electoral Violence
- IPOB/ESN Activity
- Boko Haram/ISWAP
- Communal Clashes
- Robbery/Armed Robbery
- Police/Military Operations
- Inter-Ethnic Violence
- Resource Conflicts
- Other
```

## Dependencies

- LLM Provider: Ollama (local) or OpenAI API
- `openai >= 1.0.0` - OpenAI Python client
- `httpx >= 0.24.0` - Async HTTP client for Ollama
- `pybreaker >= 1.0.0` - Circuit breaker implementation
- Redis for caching
- spaCy or transformers for entity recognition (optional enhancement)
