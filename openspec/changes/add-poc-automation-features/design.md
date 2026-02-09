# Technical Design: PoC Automation Features

## Architecture Overview

### Design Principles
1. **Proactive over Reactive**: System operates autonomously without manual intervention
2. **Self-Contained**: Minimize external dependencies (use APScheduler over Celery Beat)
3. **Observable**: Full visibility into system state and operations
4. **Resilient**: Graceful degradation and circuit breakers for external services
5. **Hybrid**: Keep production strengths (PostgreSQL, auth) while adding PoC patterns

## Component Design

### 1. APScheduler Integration

**Decision**: Use APScheduler within FastAPI lifecycle instead of separate Celery Beat process

**Rationale**:
- Self-contained: No external scheduler process needed
- Demo-friendly: One command to start everything
- Simpler deployment: Fewer moving parts
- Coexists with Celery: Can use both (APScheduler for scheduling, Celery for execution)

**Implementation Pattern**:
```python
# backend/app/main.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup_event():
    # Add 15-minute scraping job
    scheduler.add_job(
        func=automated_scrape_job,
        trigger=CronTrigger.from_crontab('*/15 * * * *'),
        id='automated_scrape',
        name='Automated news scraping',
        replace_existing=True
    )
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
```

**Trade-offs**:
- ✅ Pros: Simple, self-contained, demo-ready
- ❌ Cons: Single-instance only, not for large-scale production
- 🔄 Migration: Can coexist with Celery Beat, migrate gradually

---

### 2. High-Risk Alert System

**Decision**: File-based webhooks + database storage for alerts

**Rationale**:
- Simple: No additional message broker needed
- Fast: Direct file writes with 5-second polling
- Debug-friendly: Inspect alert files directly
- Dual storage: Files for real-time, DB for history

**Implementation Pattern**:
```python
# backend/app/services/alert_service.py
ALERT_THRESHOLD = 85
ALERT_FILE = "/data/high_risk_alerts.json"

async def check_and_alert(conflict_event):
    if conflict_event.risk_score > ALERT_THRESHOLD:
        alert = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_id': conflict_event.id,
            'title': conflict_event.title,
            'risk_score': conflict_event.risk_score,
            'location': conflict_event.location
        }
        
        # Write to file for instant UI polling
        await write_alert_webhook(alert)
        
        # Store in database for history
        await store_alert_db(alert)
        
        # Optional: Send email/Slack notification
        await send_external_notification(alert)
```

**Data Flow**:
```
Scraping → Risk Calculation → Threshold Check (>85) → Alert Generation
                                                            ↓
                                    ┌───────────────────────┴──────────────────────┐
                                    ↓                                              ↓
                            File Webhook                                     Database Storage
                         (/data/alerts.json)                              (alert_events table)
                                    ↓                                              ↓
                            UI Polling (5s)                               Historical Analysis
```

---

### 3. System Heartbeat Monitor

**Decision**: Dedicated status endpoint with scheduler metadata

**Implementation Pattern**:
```python
# backend/app/api/v1/endpoints/system.py
@router.get("/heartbeat")
async def get_system_heartbeat():
    scheduler_status = scheduler.get_job('automated_scrape')
    
    return {
        'status': 'active' if scheduler.running else 'stopped',
        'scheduler_running': scheduler.running,
        'next_run': scheduler_status.next_run_time.isoformat() if scheduler_status else None,
        'last_run': get_last_execution_time(),
        'schedule': '*/15 * * * * (Every 15 minutes)',
        'uptime': get_uptime_seconds(),
        'active_jobs': len(scheduler.get_jobs())
    }
```

**Frontend Component**:
```typescript
// frontend/src/components/dashboard/SystemHeartbeat.tsx
export function SystemHeartbeat() {
  const [heartbeat, setHeartbeat] = useState(null);
  const [countdown, setCountdown] = useState(0);
  
  useEffect(() => {
    // Poll every 10 seconds
    const interval = setInterval(async () => {
      const data = await fetch('/api/v1/system/heartbeat');
      setHeartbeat(data);
      updateCountdown(data.next_run);
    }, 10000);
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="heartbeat-monitor">
      <StatusIndicator status={heartbeat.status} />
      <NextRunCountdown seconds={countdown} />
      <LastRunTimestamp timestamp={heartbeat.last_run} />
    </div>
  );
}
```

---

### 4. LLM Integration

**Decision**: Support both Ollama (local) and OpenAI (cloud) with circuit breaker

**Rationale**:
- Ollama: Free, local, good for development
- OpenAI: Better accuracy, cloud, requires API key
- Circuit breaker: Prevent cascading failures
- Caching: Reduce API calls and costs

**Implementation Pattern**:
```python
# backend/app/services/llm_service.py
from pybreaker import CircuitBreaker
from functools import lru_cache

llm_breaker = CircuitBreaker(fail_max=5, timeout_duration=30)

class LLMService:
    def __init__(self, provider='ollama'):
        self.provider = provider
        if provider == 'ollama':
            self.client = OllamaClient(base_url='http://localhost:11434')
        else:
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    @llm_breaker
    async def extract_conflict_event(self, article_text: str):
        # Try cache first
        cache_key = f"llm:{hashlib.md5(article_text.encode()).hexdigest()}"
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        prompt = self._build_extraction_prompt(article_text)
        response = await self.client.generate(prompt, format='json')
        
        # Cache for 24 hours
        await redis_client.setex(cache_key, 86400, json.dumps(response))
        
        return response
    
    def _build_extraction_prompt(self, text: str) -> str:
        return f"""
        Extract conflict event details from this Nigerian news article.
        
        Return JSON with:
        - location: Nigerian state/LGA
        - actors: Armed groups or parties involved
        - casualties: Number of deaths/injuries
        - conflict_type: One of [Banditry, Kidnapping, Farmer-Herder, Gunmen Violence, etc]
        - severity: 1-10 scale
        - date: Event date
        
        Article:
        {text}
        
        Output valid JSON only, no explanations.
        """
```

**Circuit Breaker Behavior**:
```
Success calls → Circuit CLOSED (normal operation)
                    ↓
            5 consecutive failures
                    ↓
Circuit OPEN (fast fail, no LLM calls for 30s)
                    ↓
            After 30s timeout
                    ↓
Circuit HALF-OPEN (try one call)
        ↓                   ↓
    Success             Failure
        ↓                   ↓
    CLOSED              OPEN again
```

---

### 5. Automated Categorization

**Decision**: LLM-based classification with confidence scoring

**Implementation Pattern**:
```python
# backend/app/services/categorization_service.py

CONFLICT_ARCHETYPES = [
    'Banditry',
    'Kidnapping', 
    'Farmer-Herder Clashes',
    'Gunmen Violence',
    'Cult Violence',
    'Electoral Violence',
    'IPOB/ESN Activity',
    'Boko Haram/ISWAP',
    'Communal Clashes',
    'Other'
]

async def categorize_article(article_text: str, location: str) -> Dict:
    prompt = f"""
    Classify this Nigerian conflict article into ONE category.
    
    Categories: {', '.join(CONFLICT_ARCHETYPES)}
    
    Location context: {location}
    
    Article: {article_text}
    
    Return JSON:
    {{
        "category": "exact category from list",
        "confidence": 0-100,
        "reasoning": "brief explanation"
    }}
    """
    
    response = await llm_service.generate(prompt)
    
    # Validate category
    if response['category'] not in CONFLICT_ARCHETYPES:
        response['category'] = 'Other'
        response['confidence'] = max(0, response['confidence'] - 20)
    
    return response
```

---

### 6. Multi-Dimensional Risk Scoring

**Decision**: Weighted factor model with contextual data layers

**Implementation Pattern**:
```python
# backend/app/services/risk_service.py

class MultiDimensionalRiskCalculator:
    # Weight configuration
    WEIGHTS = {
        'event_severity': 0.40,      # Base event impact
        'climate_stress': 0.15,       # Environmental factors
        'mining_proximity': 0.15,     # Resource conflict
        'border_distance': 0.10,      # Cross-border tensions
        'economic_indicators': 0.20   # Fuel, inflation, unemployment
    }
    
    async def calculate_risk_score(self, event: ConflictEvent) -> float:
        # Base severity from casualties and conflict type
        event_severity = self._calculate_event_severity(event)
        
        # Climate stress (flood/drought indicators)
        climate_stress = await self._get_climate_stress(
            location=event.location,
            date=event.event_date
        )
        
        # Mining zone proximity
        mining_proximity = await self._calculate_mining_proximity(
            location=event.location
        )
        
        # Border distance factor
        border_distance = self._calculate_border_factor(
            location=event.location
        )
        
        # Economic indicators
        economic_indicators = await self._get_economic_stress(
            state=event.state,
            date=event.event_date
        )
        
        # Weighted sum
        risk_score = (
            event_severity * self.WEIGHTS['event_severity'] +
            climate_stress * self.WEIGHTS['climate_stress'] +
            mining_proximity * self.WEIGHTS['mining_proximity'] +
            border_distance * self.WEIGHTS['border_distance'] +
            economic_indicators * self.WEIGHTS['economic_indicators']
        )
        
        # Normalize to 0-100
        return min(100, max(0, risk_score))
```

---

### 7. Data Layer Management

**Decision**: File-based data layers with database caching

**Data Sources**:
- **Climate**: NOAA, World Bank climate API
- **Mining**: Manual curation + open datasets
- **Border**: Calculated from Nigeria boundary shapefile
- **Economic**: CBN API, NBS statistics

**Storage Pattern**:
```python
# Mock data for development, real APIs for production
CLIMATE_DATA_SOURCE = os.getenv('CLIMATE_DATA_SOURCE', 'mock')

if CLIMATE_DATA_SOURCE == 'mock':
    climate_data = load_json('/data/mock_climate_data.json')
else:
    climate_data = fetch_from_api(WORLD_BANK_CLIMATE_API)
```

---

### 8. State Management Pattern

**Decision**: Hybrid - Database for persistence, Files for real-time debugging

**File-Based State** (`/data` volume):
```
/data/
  high_risk_alerts.json        # Last 20 alerts
  automation_logs.json         # Last 100 executions
  scheduler_state.json         # Current scheduler metadata
  system_metrics.json          # Performance metrics
```

**Advantages**:
- Easy debugging (cat the file)
- Fast writes (no DB overhead)
- Shared across services (Docker volume)
- Ephemeral state (cleared on restart)

**Database State**:
- Historical alerts
- All conflict events
- User data
- Forecasts

---

## Deployment Architecture

### Docker Compose Structure

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    environment:
      - APSCHEDULER_ENABLED=true
      - LLM_PROVIDER=ollama
      - OLLAMA_URL=http://ollama:11434
    volumes:
      - shared-data:/data  # Shared state
    depends_on:
      - postgres
      - redis
      - ollama
  
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama-models:/root/.ollama
  
  frontend:
    build: ./frontend
    volumes:
      - shared-data:/data:ro  # Read-only access
  
  postgres:
    image: postgis/postgis:15-3.3
  
  redis:
    image: redis:7-alpine

volumes:
  shared-data:  # Cross-service state
  ollama-models:
  postgres-data:
```

---

## Performance Considerations

### LLM Processing
- **Batch size**: 10 articles per batch
- **Timeout**: 2 minutes per article
- **Retry**: 3 attempts with exponential backoff
- **Caching**: 24-hour Redis cache
- **Circuit breaker**: 5 failures = 30s cooldown

### Scheduler
- **Interval**: 15 minutes (balance freshness vs load)
- **Concurrency**: Single job at a time (no overlaps)
- **Timeout**: 30 minutes per scraping cycle
- **Retry**: 3 attempts on failure

### Alert Polling
- **Frontend interval**: 5 seconds
- **File size limit**: 100KB (last 20 alerts)
- **Debounce**: Prevent duplicate notifications

---

## Security Considerations

1. **LLM API Keys**: Store in environment variables, never commit
2. **File Access**: Read-only for frontend, write-only for backend
3. **Rate Limiting**: Prevent LLM API abuse
4. **Input Validation**: Sanitize article text before LLM
5. **Circuit Breaker**: Prevent DoS on external services

---

## Testing Strategy

### Unit Tests
- Scheduler service (job registration, execution)
- LLM service (mocked responses)
- Alert service (threshold detection)
- Risk calculation (all factors)

### Integration Tests
- End-to-end automation flow
- Alert triggering and display
- LLM extraction accuracy
- Frontend-backend communication

### Load Tests
- 100+ articles in batch
- Concurrent LLM calls
- Alert system under load
- Scheduler stability

---

## Monitoring & Observability

### Metrics to Track
- Scheduler uptime %
- LLM success rate
- Alert latency (detection → display)
- Categorization accuracy
- Risk score distribution

### Logging
- Structured JSON logs
- Correlation IDs per request
- LLM call metadata (tokens, latency)
- Alert trigger events

### Dashboards
- System heartbeat status
- Automation execution history
- LLM performance metrics
- Alert statistics

---

## Rollback Plan

If issues arise:
1. **Disable APScheduler**: Set `APSCHEDULER_ENABLED=false`
2. **Fall back to Celery Beat**: Existing tasks still work
3. **Disable LLM**: Set `LLM_ENABLED=false`, use rule-based extraction
4. **Disable alerts**: Set `ALERT_THRESHOLD=101` (never triggers)
5. **Remove map layers**: Hide toggles in frontend

---

## Future Enhancements

### Post-MVP Improvements
1. **WebSocket for real-time updates** (replace polling)
2. **RabbitMQ for event-driven architecture** (replace file webhooks)
3. **Distributed scheduler** (replace single-instance APScheduler)
4. **Advanced LLM features** (fine-tuning, RAG)
5. **Chat interface** (natural language queries)

### Scalability Path
1. Use APScheduler for MVP/demos
2. Migrate to Celery Beat for production scale
3. Add load balancing for LLM calls
4. Implement horizontal scaling for backend
5. Use Kubernetes for orchestration
