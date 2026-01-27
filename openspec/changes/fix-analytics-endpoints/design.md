# Analytics Endpoints Technical Design

## Architecture Overview

The analytics system provides advanced conflict data analysis through RESTful endpoints that query the Neon PostgreSQL database and return aggregated insights for the Nigeria Conflict Tracker dashboard.

## Current System Architecture

```
Frontend (Vercel) → API Gateway → FastAPI Backend (Railway) → Neon PostgreSQL
                                        ↓
                                Analytics Endpoints
                                /api/v1/analytics/*
```

## Problem Analysis

### Working Components ✅
- **Database Layer:** Neon PostgreSQL with `conflict_events` table (6,980 records)
- **Authentication:** JWT-based auth with RBAC (viewer role permissions)
- **Basic Endpoints:** `/api/dashboard/stats` working correctly
- **Infrastructure:** Vercel + Railway deployment operational

### Failing Components ❌
- **Analytics Endpoints:** All `/api/v1/analytics/*` return 500 Internal Server Error
- **Error Visibility:** No detailed error logging or monitoring
- **Query Complexity:** Advanced aggregations may be causing failures

## Root Cause Hypothesis

Based on investigation, the most likely causes are:

1. **SQLAlchemy Session Issues:**
   - Improper session lifecycle management
   - Connection pooling problems
   - Transaction rollback issues

2. **Query Complexity:**
   - Advanced aggregations failing under load
   - Date filtering with timezone problems
   - Large dataset processing issues

3. **Error Handling:**
   - Missing try-catch blocks hiding actual errors
   - Poor error propagation to logs
   - No graceful degradation

## Proposed Solution Architecture

### Enhanced Error Handling Layer

```python
# Error handling wrapper for all analytics endpoints
class AnalyticsErrorHandler:
    @staticmethod
    def handle_analytics_request(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                logger.info(f"Analytics request: {func.__name__}")
                start_time = time.time()
                
                result = await func(*args, **kwargs)
                
                duration = time.time() - start_time
                logger.info(f"Analytics success: {func.__name__} ({duration:.2f}s)")
                return result
                
            except SQLAlchemyError as e:
                logger.error(f"Database error in {func.__name__}: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            except ValueError as e:
                logger.error(f"Data validation error in {func.__name__}: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
        return wrapper
```

### Database Query Optimization

```python
# Optimized query patterns for analytics
class AnalyticsQueries:
    @staticmethod
    def get_dashboard_summary(db: Session, days: int = 180):
        """Optimized dashboard summary with proper error handling"""
        try:
            cutoff_date = datetime.now().date() - timedelta(days=days)
            
            # Use explicit column selection instead of *
            summary_query = db.query(
                func.count(ConflictEvent.id).label('total_incidents'),
                func.sum(ConflictEvent.fatalities).label('total_fatalities'),
                func.sum(ConflictEvent.injured).label('total_injuries'),
                func.count(func.distinct(ConflictEvent.state)).label('states_affected')
            ).filter(ConflictEvent.event_date >= cutoff_date)
            
            result = summary_query.one()
            
            return {
                "total_incidents": result.total_incidents or 0,
                "total_fatalities": result.total_fatalities or 0,
                "total_injuries": result.total_injuries or 0,
                "states_affected": result.states_affected or 0
            }
            
        except Exception as e:
            logger.error(f"Dashboard summary query failed: {str(e)}")
            raise
```

### Session Management Enhancement

```python
# Enhanced database dependency with proper session management
@contextmanager
def get_analytics_db():
    """Analytics-specific database session with enhanced error handling"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        db.close()

# Usage in endpoints
@router.get("/dashboard-summary")
@AnalyticsErrorHandler.handle_analytics_request
async def get_dashboard_summary(
    current_user: User = Depends(require_role("viewer"))
):
    with get_analytics_db() as db:
        result = AnalyticsQueries.get_dashboard_summary(db)
        return result
```

## Data Models & Schemas

### Input Validation

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class AnalyticsRequest(BaseModel):
    """Base analytics request with common parameters"""
    start_date: Optional[date] = Field(None, description="Filter start date")
    end_date: Optional[date] = Field(None, description="Filter end date") 
    states: Optional[list[str]] = Field(None, description="Filter by states")
    limit: Optional[int] = Field(100, ge=1, le=1000, description="Result limit")

class HotspotsRequest(AnalyticsRequest):
    """Hotspots-specific request parameters"""
    min_incidents: int = Field(5, ge=1, description="Minimum incidents threshold")
    radius_km: Optional[int] = Field(50, ge=1, le=500, description="Radius in kilometers")
```

### Response Schemas

```python
class DashboardSummaryResponse(BaseModel):
    """Standardized dashboard summary response"""
    total_incidents: int
    total_fatalities: int
    total_injuries: int
    states_affected: int
    period_days: int
    last_updated: str
    data_freshness: str = "real-time"

class ConflictHotspot(BaseModel):
    """Individual hotspot data"""
    state: str
    lga: str  
    incident_count: int
    total_fatalities: int
    total_displaced: int
    severity_score: float

class HotspotsResponse(BaseModel):
    """Hotspots endpoint response"""
    hotspots: list[ConflictHotspot]
    total_hotspots: int
    criteria: dict
    generated_at: str
```

## Performance Optimizations

### Query Optimization Strategies

1. **Index Usage:**
   ```sql
   -- Ensure these indexes exist for optimal query performance
   CREATE INDEX IF NOT EXISTS idx_conflict_events_date_state ON conflict_events(event_date, state);
   CREATE INDEX IF NOT EXISTS idx_conflict_events_lga_date ON conflict_events(lga, event_date);
   ```

2. **Query Batching:**
   ```python
   # Process large aggregations in batches
   def get_large_aggregation(db: Session, batch_size: int = 1000):
       offset = 0
       results = []
       
       while True:
           batch = db.query(ConflictEvent)\
                    .offset(offset)\
                    .limit(batch_size)\
                    .all()
           
           if not batch:
               break
               
           results.extend(batch)
           offset += batch_size
           
       return results
   ```

3. **Caching Strategy:**
   ```python
   from functools import lru_cache
   import redis
   
   redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))
   
   @lru_cache(maxsize=128)
   def cached_dashboard_summary(days: int, cache_key: str):
       """Cache expensive dashboard calculations"""
       cached_result = redis_client.get(cache_key)
       if cached_result:
           return json.loads(cached_result)
       
       # Perform expensive calculation
       result = calculate_dashboard_summary(days)
       
       # Cache for 10 minutes
       redis_client.setex(cache_key, 600, json.dumps(result))
       return result
   ```

## Testing Strategy

### Unit Testing Approach

```python
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

class TestAnalyticsEndpoints:
    @pytest.fixture
    def mock_db(self):
        """Mock database session for testing"""
        db = Mock()
        # Configure mock responses
        return db
    
    @pytest.fixture  
    def authenticated_client(self):
        """Test client with valid authentication"""
        client = TestClient(app)
        # Add authentication headers
        return client
    
    def test_dashboard_summary_success(self, authenticated_client, mock_db):
        """Test successful dashboard summary request"""
        response = authenticated_client.get("/api/v1/analytics/dashboard-summary")
        assert response.status_code == 200
        assert "total_incidents" in response.json()
    
    def test_dashboard_summary_no_data(self, authenticated_client, mock_db):
        """Test dashboard summary with no data"""
        # Mock empty result
        mock_db.query().filter().one.return_value = Mock(
            total_incidents=0,
            total_fatalities=0,
            total_injuries=0,
            states_affected=0
        )
        
        response = authenticated_client.get("/api/v1/analytics/dashboard-summary")
        assert response.status_code == 200
        assert response.json()["total_incidents"] == 0
```

### Integration Testing

```python
@pytest.mark.integration
class TestAnalyticsIntegration:
    """Integration tests with real database"""
    
    def test_real_database_connection(self):
        """Test actual database connectivity"""
        with get_analytics_db() as db:
            result = db.query(ConflictEvent).count()
            assert result > 0
    
    def test_end_to_end_analytics_flow(self, test_user_token):
        """Test complete analytics workflow"""
        # 1. Authenticate
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # 2. Request analytics
        response = client.get("/api/v1/analytics/dashboard-summary", headers=headers)
        
        # 3. Validate response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["total_incidents"], int)
        assert data["total_incidents"] >= 0
```

## Monitoring & Observability

### Logging Strategy

```python
import structlog

logger = structlog.get_logger("analytics")

def log_analytics_request(endpoint: str, user_id: str, duration: float, status: str):
    """Structured logging for analytics requests"""
    logger.info(
        "analytics_request",
        endpoint=endpoint,
        user_id=user_id,
        duration_ms=duration * 1000,
        status=status,
        timestamp=datetime.utcnow().isoformat()
    )
```

### Metrics Collection

```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics for monitoring
analytics_requests_total = Counter(
    "analytics_requests_total",
    "Total analytics requests",
    ["endpoint", "status"]
)

analytics_request_duration = Histogram(
    "analytics_request_duration_seconds",
    "Analytics request duration",
    ["endpoint"]
)

active_database_connections = Gauge(
    "analytics_db_connections_active",
    "Active database connections for analytics"
)
```

## Security Considerations

### Input Validation

```python
from fastapi import Query
from datetime import date, timedelta

@router.get("/hotspots")
async def get_hotspots(
    min_incidents: int = Query(5, ge=1, le=1000, description="Minimum incidents"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    current_user: User = Depends(require_role("viewer"))
):
    # Validate date range
    if start_date and end_date:
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="Start date must be before end date")
        
        max_range = timedelta(days=1095)  # 3 years max
        if end_date - start_date > max_range:
            raise HTTPException(status_code=400, detail="Date range too large (max 3 years)")
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.get("/dashboard-summary")
@limiter.limit("30/minute")  # Limit expensive analytics requests
async def get_dashboard_summary(request: Request, ...):
    # Analytics endpoint implementation
    pass
```

## Deployment Considerations

### Environment Configuration

```python
class AnalyticsSettings(BaseSettings):
    """Analytics-specific configuration"""
    analytics_query_timeout: int = Field(30, env="ANALYTICS_QUERY_TIMEOUT")
    analytics_cache_ttl: int = Field(600, env="ANALYTICS_CACHE_TTL")
    analytics_max_results: int = Field(1000, env="ANALYTICS_MAX_RESULTS")
    analytics_db_pool_size: int = Field(10, env="ANALYTICS_DB_POOL_SIZE")
```

### Health Checks

```python
@router.get("/health")
async def analytics_health_check():
    """Analytics-specific health check"""
    checks = {
        "database": False,
        "redis": False,
        "query_performance": False
    }
    
    try:
        # Test database connectivity
        with get_analytics_db() as db:
            db.execute("SELECT 1").fetchone()
            checks["database"] = True
        
        # Test Redis connectivity  
        redis_client.ping()
        checks["redis"] = True
        
        # Test query performance
        start_time = time.time()
        with get_analytics_db() as db:
            db.query(ConflictEvent).limit(1).first()
        duration = time.time() - start_time
        checks["query_performance"] = duration < 1.0  # Under 1 second
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
    
    return {
        "status": "healthy" if all(checks.values()) else "unhealthy",
        "checks": checks
    }
```

---

## Implementation Priority

### Phase 1 (Critical)
1. Enhanced error handling and logging
2. Database session management fixes  
3. Basic query validation

### Phase 2 (Important)
1. Performance optimization
2. Comprehensive testing
3. Monitoring implementation

### Phase 3 (Nice-to-have)
1. Advanced caching
2. Query optimization
3. Documentation updates

---

**Design Status:** Ready for Implementation  
**Estimated Implementation Time:** 8-12 hours
**Risk Level:** Low (isolated changes, easy rollback)