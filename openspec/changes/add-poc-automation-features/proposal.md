# Change: Add PoC Automation Features (Hybrid Approach)

## Why

After analyzing the PoC repository (https://github.com/Ejyke90/nextier-nigeria-violent-conflicts-database), we identified 15 critical features that enable autonomous operation and proactive intelligence. The current app has superior production infrastructure (PostgreSQL, authentication, forecasting) but lacks the automation-first patterns that make the PoC demo-ready and operationally transparent.

**Problem:**
- Current app requires manual intervention and external process management (Celery Beat)
- No real-time operational visibility for users
- No instant alerting for high-risk events
- No automated intelligence extraction from unstructured text
- Limited observability of system health

**Opportunity:**
Merge PoC's automation patterns with current app's production infrastructure to create a best-of-both-worlds solution that is both demo-ready and production-grade.

## What Changes

### Phase 1: Critical Automation (HIGH PRIORITY) 🔴
- **Add APScheduler integration** into FastAPI lifecycle for self-contained scheduling
- **Add high-risk alert system** with threshold detection (risk_score > 85)
- **Add system heartbeat monitor** with real-time status and countdown timer
- **Add automation execution logging** with structured audit trail

### Phase 2: Intelligence Upgrade (HIGH PRIORITY) 🔴
- **Add LLM integration** (Ollama/OpenAI) for event extraction from news text
- **Add automated categorization** service with conflict archetype classification
- **Add confidence scoring** for categorization results
- **Add batch processing** for LLM operations

### Phase 3: Enhanced Risk Assessment (MEDIUM PRIORITY) 🟡
- **Add climate stress data layer** integration
- **Add mining zone data layer** for proximity analysis
- **Add border proximity calculations** to risk scoring
- **Add interactive map layers** with toggle controls

### Phase 4: User Experience Polish (MEDIUM PRIORITY) 🟡
- **Add live signal ticker** component for real-time updates
- **Add policymaker dashboard** with executive summaries
- **Add chat interface** for natural language data queries (optional)
- **Add WebSocket support** for instant UI updates (replaces polling)

### Infrastructure Changes
- **BREAKING**: Add APScheduler dependency to FastAPI
- **BREAKING**: Add Ollama or OpenAI API integration
- Add file-based state management for debugging (`/data` volume pattern)
- Add circuit breaker pattern for external service calls
- Enhance docker-compose for one-command deployment

## Impact

### Affected Specs
- **dashboard-monitoring** (MODIFIED) - Add heartbeat, alerts, ticker
- **realtime-monitoring** (MODIFIED) - Add automated scheduler status
- **intelligence-extraction** (NEW) - LLM-powered event extraction
- **risk-assessment** (MODIFIED) - Multi-dimensional risk factors
- **automation-scheduler** (NEW) - APScheduler integration

### Affected Code
- `backend/app/main.py` - FastAPI lifecycle integration
- `backend/app/tasks/` - New scheduler service, LLM service
- `backend/app/api/v1/endpoints/` - New automation, intelligence endpoints
- `backend/app/services/` - New LLM, categorization, alert services
- `frontend/src/components/dashboard/` - New UI components
- `docker-compose.yml` - Enhanced orchestration

### Breaking Changes
- **BREAKING**: Requires Ollama installation or OpenAI API key
- **BREAKING**: New environment variables for LLM configuration
- **BREAKING**: APScheduler conflicts with existing Celery Beat patterns (migration path provided)

### Migration Path
1. Deploy APScheduler alongside Celery Beat (both can coexist)
2. Gradually migrate scheduled tasks from Celery Beat to APScheduler
3. Optionally keep Celery for heavy processing, use APScheduler for scheduling
4. Or keep Celery Beat for production, use APScheduler for demos/dev

## Success Criteria

### Phase 1 Complete When:
- ✅ System runs autonomously without manual intervention
- ✅ High-risk alerts appear in UI within 5 seconds of detection
- ✅ System heartbeat shows live status with countdown timer
- ✅ Automation logs track all executions with >95% accuracy

### Phase 2 Complete When:
- ✅ LLM extracts structured events from news articles with >80% accuracy
- ✅ Automated categorization achieves >85% confidence on test set
- ✅ LLM processing completes within 2 minutes per article
- ✅ Batch processing handles 100+ articles without failures

### Phase 3 Complete When:
- ✅ Multi-dimensional risk scores incorporate 3+ data layers
- ✅ Map displays climate, mining, border layers with toggle controls
- ✅ Risk scores show measurable improvement in prediction accuracy

### Phase 4 Complete When:
- ✅ UI updates in real-time (<5 second latency)
- ✅ Policymaker dashboard displays actionable insights
- ✅ One-command deployment works on fresh system
- ✅ Demo can run without technical intervention

## Dependencies

### Required
- Python 3.11+
- FastAPI 0.104+
- APScheduler 3.10+
- Ollama (local) OR OpenAI API key
- PostgreSQL with PostGIS (existing)

### Optional
- RabbitMQ (for advanced event-driven patterns)
- WebSocket support (for real-time updates)
- Redis (existing, for caching LLM results)

## Risks & Mitigations

### Risk 1: LLM Cost/Latency
**Mitigation:**
- Use local Ollama for development (free)
- Implement aggressive caching (Redis)
- Batch processing to reduce API calls
- Async processing to prevent blocking

### Risk 2: APScheduler Single-Instance Limitation
**Mitigation:**
- Use for demos and MVP
- Keep Celery Beat option for production scale
- Document migration path clearly
- Provide toggle configuration

### Risk 3: Integration Complexity
**Mitigation:**
- Phased rollout (4 phases over 8 weeks)
- Feature flags for gradual enablement
- Comprehensive testing per phase
- Rollback procedures documented

### Risk 4: Data Layer Availability
**Mitigation:**
- Start with mock data for climate/mining layers
- Source real data gradually
- Fallback to existing risk scoring if layers unavailable
- Document data source requirements

## Timeline Estimate

- **Phase 1:** 2 weeks (Critical automation)
- **Phase 2:** 2 weeks (Intelligence upgrade)
- **Phase 3:** 2 weeks (Risk assessment)
- **Phase 4:** 2 weeks (UX polish)

**Total:** 8 weeks for full implementation

**MVP (Phases 1+2 only):** 4 weeks for demo-ready automation + intelligence
