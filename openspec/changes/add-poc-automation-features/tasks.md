# Implementation Tasks

## Phase 1: Critical Automation (Week 1-2)

### 1.1 APScheduler Integration
- [ ] Add APScheduler dependency to `backend/requirements.txt`
- [ ] Create `backend/app/services/scheduler_service.py`
- [ ] Integrate scheduler into FastAPI lifecycle in `main.py`
- [ ] Add 15-minute cron job for automated scraping
- [ ] Add scheduler health check endpoint
- [ ] Add scheduler status endpoint (`/api/v1/scheduler/status`)
- [ ] Add scheduler control endpoints (start/stop/trigger)
- [ ] Test scheduler persistence and recovery
- [ ] Document scheduler configuration

### 1.2 High-Risk Alert System
- [ ] Create `backend/app/services/alert_service.py`
- [ ] Add risk threshold detection (score > 85)
- [ ] Create alert webhook mechanism (file-based)
- [ ] Add alert storage model to database
- [ ] Create alert API endpoints (`/api/v1/alerts`)
- [ ] Add frontend alert monitor component
- [ ] Add toast notification system
- [ ] Implement 5-second polling for alerts
- [ ] Test alert triggering and display

### 1.3 System Heartbeat Monitor
- [ ] Create `frontend/src/components/dashboard/SystemHeartbeat.tsx`
- [ ] Add backend endpoint `/api/v1/system/heartbeat`
- [ ] Display scheduler status (running/stopped)
- [ ] Show next run countdown timer
- [ ] Show last successful run timestamp
- [ ] Add visual health indicators
- [ ] Integrate into main dashboard
- [ ] Test real-time updates

### 1.4 Automation Execution Logs
- [ ] Create automation log model
- [ ] Add logging to scraping tasks
- [ ] Create `/api/v1/automation/logs` endpoint
- [ ] Add log retention policy (last 100 entries)
- [ ] Create log viewer component
- [ ] Add filtering and search
- [ ] Test log accuracy and completeness

## Phase 2: Intelligence Upgrade (Week 3-4)

### 2.1 LLM Integration
- [ ] Add Ollama/OpenAI client to `backend/requirements.txt`
- [ ] Create `backend/app/services/llm_service.py`
- [ ] Implement event extraction prompts
- [ ] Add LLM configuration (model, endpoint)
- [ ] Implement circuit breaker for LLM calls
- [ ] Add retry mechanism with exponential backoff
- [ ] Add LLM response caching (Redis)
- [ ] Test with sample articles
- [ ] Document LLM setup and configuration

### 2.2 Automated Categorization
- [ ] Create `backend/app/services/categorization_service.py`
- [ ] Define conflict archetype taxonomy
- [ ] Create categorization prompts
- [ ] Implement confidence scoring
- [ ] Add batch processing capability
- [ ] Create categorization API endpoints
- [ ] Add categorization to scraping pipeline
- [ ] Test accuracy on labeled dataset
- [ ] Document categorization logic

### 2.3 Event Extraction Pipeline
- [ ] Create structured event extraction logic
- [ ] Add entity recognition (locations, actors)
- [ ] Extract casualty counts
- [ ] Extract conflict types
- [ ] Validate extracted data
- [ ] Store extracted events in database
- [ ] Create events API endpoints
- [ ] Test extraction accuracy
- [ ] Monitor extraction performance

### 2.4 Intelligence Dashboard
- [ ] Create categorization stats component
- [ ] Create archetype distribution chart
- [ ] Add confidence metrics display
- [ ] Create intelligence depth indicators
- [ ] Integrate with existing dashboard
- [ ] Test data updates

## Phase 3: Enhanced Risk Assessment (Week 5-6)

### 3.1 Climate Data Layer
- [ ] Source climate stress data (flood, drought)
- [ ] Create climate data model
- [ ] Create climate data import script
- [ ] Add climate data API endpoints
- [ ] Create climate overlay component
- [ ] Integrate climate data into risk scoring
- [ ] Test climate layer visualization

### 3.2 Mining Zone Layer
- [ ] Source mining zone data (illegal mining areas)
- [ ] Create mining zone model
- [ ] Create mining zone import script
- [ ] Add mining proximity calculations
- [ ] Create mining overlay component
- [ ] Integrate mining data into risk scoring
- [ ] Test mining layer visualization

### 3.3 Border Proximity Layer
- [ ] Calculate distances to international borders
- [ ] Create border proximity scoring function
- [ ] Integrate border data into risk model
- [ ] Create border zone visualization
- [ ] Test border proximity calculations

### 3.4 Multi-Dimensional Risk Model
- [ ] Enhance risk calculation algorithm
- [ ] Add weighted factors (climate, mining, border, economic)
- [ ] Implement contextual scoring
- [ ] Update risk API endpoints
- [ ] Test risk score improvements
- [ ] Document risk methodology

### 3.5 Interactive Map Layers
- [ ] Create layer toggle component
- [ ] Add climate stress layer control
- [ ] Add mining zone layer control
- [ ] Add border proximity layer control
- [ ] Add economic indicator overlays
- [ ] Implement layer visibility persistence
- [ ] Test layer interactions

## Phase 4: User Experience Polish (Week 7-8)

### 4.1 Live Signal Ticker
- [ ] Create `frontend/src/components/dashboard/LiveSignalTicker.tsx`
- [ ] Implement scrolling ticker animation
- [ ] Add color-coding by severity
- [ ] Add 5-second auto-refresh
- [ ] Integrate with dashboard
- [ ] Test ticker performance

### 4.2 Policymaker Dashboard
- [ ] Create `frontend/src/components/dashboard/PolicymakerAlert.tsx`
- [ ] Generate executive summaries
- [ ] Add actionable recommendations
- [ ] Create priority ranking
- [ ] Add trend analysis view
- [ ] Test with stakeholder feedback

### 4.3 WebSocket Real-Time Updates (Optional)
- [ ] Add WebSocket support to FastAPI
- [ ] Create WebSocket connection manager
- [ ] Add real-time event broadcasting
- [ ] Update frontend to use WebSocket
- [ ] Fallback to polling if WebSocket fails
- [ ] Test WebSocket reliability

### 4.4 Chat Interface (Optional)
- [ ] Create chat component
- [ ] Add natural language query parser
- [ ] Integrate LLM for query responses
- [ ] Add context-aware responses
- [ ] Test query accuracy

### 4.5 One-Command Deployment
- [ ] Enhance docker-compose.yml
- [ ] Add all services to compose
- [ ] Configure shared volumes
- [ ] Add health checks
- [ ] Create demo-start script
- [ ] Test on fresh system
- [ ] Document deployment process

## Infrastructure & DevOps

### 5.1 Dependencies
- [ ] Update requirements.txt with new packages
- [ ] Update package.json with new frontend deps
- [ ] Test dependency installation
- [ ] Update deployment documentation

### 5.2 Environment Configuration
- [ ] Add LLM configuration variables
- [ ] Add scheduler configuration variables
- [ ] Add alert threshold configuration
- [ ] Document all new environment variables
- [ ] Update .env.example

### 5.3 Database Migrations
- [ ] Create alert storage table migration
- [ ] Create automation log table migration
- [ ] Create extracted events table migration
- [ ] Create categorization table migration
- [ ] Test migrations up and down

### 5.4 Testing
- [ ] Write unit tests for scheduler service
- [ ] Write unit tests for LLM service
- [ ] Write unit tests for alert service
- [ ] Write integration tests for automation pipeline
- [ ] Write frontend component tests
- [ ] Run full test suite

### 5.5 Documentation
- [ ] Update README with new features
- [ ] Document LLM setup (Ollama vs OpenAI)
- [ ] Document scheduler configuration
- [ ] Document alert system
- [ ] Create user guide for new features
- [ ] Update deployment guide

## Validation Checklist

### Phase 1 Validation
- [ ] System runs autonomously for 24 hours without intervention
- [ ] High-risk alerts appear within 5 seconds
- [ ] Heartbeat shows accurate status
- [ ] Automation logs track all executions

### Phase 2 Validation
- [ ] LLM extraction accuracy >80%
- [ ] Categorization confidence >85%
- [ ] Processing time <2 min per article
- [ ] Batch processing handles 100+ articles

### Phase 3 Validation
- [ ] Risk scores incorporate 3+ data layers
- [ ] Map layers display correctly
- [ ] Layer toggles work smoothly
- [ ] Risk predictions show improvement

### Phase 4 Validation
- [ ] UI updates with <5 second latency
- [ ] Policymaker dashboard displays insights
- [ ] One-command deployment works
- [ ] Demo runs without technical intervention

## Total Tasks: 141
