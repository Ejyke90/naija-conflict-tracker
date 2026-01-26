# Project Context

## Purpose
**Nextier Nigeria Violent Conflicts Database** - A production-grade conflict tracking platform that monitors violent conflicts across all 36 Nigerian states using historical data, real-time news scraping, and AI-powered predictive analytics.

**Mission:** Provide comprehensive, real-time visibility of organized violence (armed groups, insurgencies, communal clashes) to support security analysts, researchers, government officials, NGOs, and humanitarian workers.

**Current State:** 65% production-ready with strong ML/geospatial foundation  
**Target State:** 100% production-ready with enterprise security, WCAG 2.1 AA compliance, comprehensive testing

## Tech Stack

### Backend
- **Framework:** Python 3.11+ with FastAPI (async/await)
- **Database:** PostgreSQL 15+ with PostGIS (geospatial) + TimescaleDB (time-series)
- **Cache:** Redis 7+ (forecast caching, session store)
- **Task Queue:** Celery with Redis broker (automated scraping, forecasting)
- **ML/AI:** Prophet, statsmodels (ARIMA), scikit-learn, Groq LLM API
- **Scraping:** BeautifulSoup4, Feedparser (RSS), custom politeness layer
- **Reporting:** ReportLab (PDF generation)
- **ORM:** SQLAlchemy with async support
- **Testing:** pytest, pytest-asyncio, pytest-cov

### Frontend
- **Framework:** Next.js 14+ (React 18+, App Router)
- **UI Library:** Radix UI + Tailwind CSS + Shadcn/ui components
- **Maps:** Mapbox GL JS (clustering, heat maps, vector tiles)
- **Charts:** Recharts, D3.js (time-series visualizations)
- **Data Fetching:** SWR (stale-while-revalidate)
- **Forms:** React Hook Form + Zod validation
- **State:** React Context API
- **Testing:** Jest, React Testing Library, Cypress (E2E)

### Infrastructure
- **Containerization:** Docker + docker-compose
- **Backend Deploy:** Railway (PostgreSQL + Redis + FastAPI)
- **Frontend Deploy:** Vercel (Edge Network, auto-scaling)
- **CI/CD:** GitHub Actions (planned - not yet implemented)
- **Monitoring:** Planned (Sentry, UptimeRobot)
- **Secrets:** Environment variables (Railway Secrets, Vercel Env)

## Project Conventions

### Code Style
**Backend (Python):**
- PEP 8 compliance with Black formatter (line length: 100)
- Type hints required for all function signatures
- Async/await for I/O operations
- Pydantic models for request/response validation
- Docstrings: Google style for classes and functions
- Import order: standard library → third-party → local (isort)

**Frontend (TypeScript):**
- ESLint + Prettier (2-space indentation)
- Functional components with hooks (no class components)
- TypeScript strict mode enabled
- Named exports preferred over default exports
- File naming: kebab-case for components, camelCase for utilities
- CSS: Tailwind utility classes, avoid custom CSS when possible

### Architecture Patterns
**Backend:**
- **Layered Architecture:** Routes → Services → Models → Database
- **Repository Pattern:** Database access abstracted via repositories
- **Dependency Injection:** FastAPI dependencies for shared resources
- **Event-Driven:** Celery tasks for background processing (scraping, forecasting)
- **Caching Strategy:** Redis with TTL (forecasts: 1hr, states: 24hr)

**Frontend:**
- **Component Structure:** Pages → Components → Hooks → Utils
- **Data Fetching:** SWR for server state, React Context for UI state
- **Routing:** Next.js App Router (file-based routing)
- **Error Handling:** Error boundaries + fallback UI
- **Performance:** Code splitting, lazy loading, image optimization

**Geospatial:**
- **Coordinate System:** WGS84 (EPSG:4326) for all geographic data
- **PostGIS Functions:** ST_Within, ST_DWithin for spatial queries
- **Geocoding:** Custom Nigerian geocoder (774 LGAs, 10,000+ villages)

### Testing Strategy
**Current State:** Minimal testing (<10% coverage) - **CRITICAL GAP**

**Target:**
- **Backend Unit Tests:** ≥80% coverage (pytest + pytest-cov)
- **Frontend Unit Tests:** ≥70% coverage (Jest + React Testing Library)
- **E2E Tests:** Cypress (≥15 critical user flows)
- **Performance Tests:** k6 (1,000 concurrent users, <2s page load)
- **Accessibility Tests:** axe-core (WCAG 2.1 AA compliance)

**Test Organization:**
- Backend: `backend/tests/test_*.py` (mirror app structure)
- Frontend: `frontend/__tests__/` or co-located `*.test.tsx`
- E2E: `frontend/cypress/e2e/*.cy.ts`

### Git Workflow
- **Main Branch:** `main` (production-ready code only)
- **Development:** Feature branches from `main` (`feature/auth-system`, `fix/map-performance`)
- **Commit Convention:** Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`)
- **PR Requirements:** Passing tests (when CI/CD is set up), code review, no merge conflicts
- **Versioning:** Semantic versioning for releases

## Domain Context

### Nigerian Geography
- **Coverage:** All 36 states + Federal Capital Territory (FCT)
- **Administrative Levels:** State → LGA (Local Government Area, 774 total) → Community (10,000+ villages)
- **Regions:** North-West, North-East, North-Central, South-West, South-East, South-South

### Conflict Typology
**Focus:** Organized violence (NOT individual crimes)
- **Armed Insurgency:** Boko Haram, ISWAP, bandits
- **Communal Clashes:** Farmer-herder conflicts, ethnic tensions
- **Cult Violence:** Campus/urban cult groups
- **Political Violence:** Election-related violence
- **Criminal Gangs:** Kidnapping syndicates, armed robbery

### Data Sources
- **News Scraping:** 15+ Nigerian outlets (Punch, Vanguard, Daily Trust, Premium Times, etc.)
- **Historical Database:** Nextier's curated Excel database (2017-2024)
- **Social Media:** Twitter/X monitoring (schema exists, not yet active)
- **Poverty Data:** World Bank, NBS (Nigerian Bureau of Statistics)

### Key Metrics (ACLED-Style)
- **Deadliness Index:** Conflict intensity by fatalities
- **Civilian Danger Index:** Risk to non-combatants
- **Diffusion Index:** Geographic spread of violence
- **Fragmentation Index:** Number of active armed groups per state

### User Personas
1. **Security Analysts** - Monitor trends, identify hotspots, generate reports
2. **Researchers** - Academic studies, historical analysis, data exports
3. **Government Officials** - Regional risk assessment, policy planning
4. **NGO/Humanitarian Workers** - Intervention planning, resource allocation
5. **Journalists** - Investigation, fact-checking, conflict patterns

## Important Constraints

### Technical Constraints
- **Performance:** Must work on 3G connections (page load <2s, API <500ms)
- **Scalability:** Support 1,000 concurrent users (current: ~10-50)
- **Database Size:** 10,000+ conflict records, growing daily
- **Map Rendering:** Handle clustering for dense conflict areas (Lagos, Borno, Kaduna)
- **ML Inference:** Prophet models can be compute-intensive (caching required)

### Legal/Compliance
- **Accessibility:** WCAG 2.1 AA compliance required (legal requirement in many jurisdictions)
- **Data Privacy:** NDPR (Nigerian Data Protection Regulation) compliance
- **GDPR:** If EU users access the platform
- **Conflict Data:** Public information (news-based), no sensitive sources

### Security Constraints
- **No Authentication:** Currently NO auth system - **BLOCKING PRODUCTION**
- **Public API:** All endpoints currently open (security risk)
- **Rate Limiting:** Not implemented (DDoS vulnerability)
- **Input Validation:** Partial (needs comprehensive Pydantic schemas)

### Business Constraints
- **Budget:** Limited resources (open-source/NGO project)
- **Deployment:** Free/low-cost tiers (Railway, Vercel)
- **Maintenance:** Small team (2-3 developers)
- **Timeline:** 16-20 weeks to production-ready

### Data Quality Constraints
- **Geocoding Accuracy:** Must achieve ≥90% precision for Nigerian locations
- **Deduplication:** News sources overlap - must detect duplicates
- **NLP Extraction:** Entity extraction accuracy critical for data quality
- **Forecast Reliability:** MAE (Mean Absolute Error) target: <3 incidents/week

## External Dependencies

### AI/ML Services
- **Groq API:** LLM for NLP entity extraction (location, actors, event types)
  - API Key: Required in `.env`
  - Rate Limit: Monitor usage
  - Fallback: Manual extraction if quota exceeded

### Geospatial Services
- **Mapbox GL JS:** Interactive maps, geocoding, basemaps
  - Public Access Token: Required for frontend
  - Tile Loading: Vector tiles for performance
  - Pricing: Generous free tier (50,000 loads/month)

### Database Extensions
- **PostGIS:** Spatial queries, geographic indexing
  - Version: 3.3+
  - Functions Used: ST_Within, ST_DWithin, ST_Distance, ST_MakePoint
- **TimescaleDB:** Time-series optimization for `conflicts` and `social_chatter` tables
  - Hypertables: Automatic partitioning by `event_date`
  - Retention: Planned (archive old data after 5 years)

### News Sources (RSS Feeds)
- **Punch Nigeria** (https://punchng.com)
- **Vanguard News** (https://www.vanguardngr.com)
- **Daily Trust** (https://dailytrust.com)
- **Premium Times** (https://www.premiumtimesng.com)
- **The Cable** (https://www.thecable.ng)
- **Sahara Reporters** (http://saharareporters.com)
- **Channels TV** (https://www.channelstv.com)
- **Leadership** (https://leadership.ng)
- **Blueprint** (https://www.blueprint.ng)
- **Nigerian Tribune** (https://tribuneonlineng.com)
- 5+ additional regional sources

**Scraping Constraints:**
- Respectful crawling (politeness delays: 2-5 seconds per domain)
- Rate limiting compliance
- robots.txt adherence
- Error handling for site downtime

### Cloud Services
- **Railway:** Backend hosting (PostgreSQL, Redis, FastAPI)
  - Free tier: Limited resources
  - Auto-scaling: Not enabled (manual scaling)
- **Vercel:** Frontend hosting (Next.js)
  - Edge Network: Global CDN
  - Auto-scaling: Enabled
  - Build minutes: Monitor usage

### Monitoring (Planned)
- **Sentry:** Error tracking and performance monitoring
- **UptimeRobot:** Uptime monitoring and alerting
- **Lighthouse CI:** Performance and accessibility audits

## Existing Features (Do Not Modify)

The following features are **already implemented and working well** - OpenSpec changes should NOT recreate these:

✅ **Machine Learning Forecasting** - Prophet, ARIMA, Ensemble models with confidence intervals  
✅ **RSS News Scraping** - 15+ Nigerian sources with automated Celery scheduling  
✅ **NLP Entity Extraction** - Groq LLM for location/actor/event extraction  
✅ **Geospatial Analysis** - PostGIS queries, hotspot detection, proximity searches  
✅ **TimescaleDB Optimization** - Time-series hypertables for conflicts & social_chatter  
✅ **Interactive Maps** - Mapbox GL JS with clustering, heat maps, popups  
✅ **Dashboard Visualizations** - Recharts/D3.js charts, time-series analysis  
✅ **ACLED-Style Metrics** - Deadliness, civilian danger, diffusion, fragmentation indices  
✅ **Gender-Disaggregated Data** - Male/female/unknown casualty tracking  
✅ **Celery Task Scheduling** - Automated scraping (6hrs), forecasting (daily)  
✅ **Redis Caching** - Forecast caching (1hr TTL), state data (24hr TTL)  
✅ **Docker Containerization** - docker-compose for local development  
✅ **Production Deployments** - Railway (backend), Vercel (frontend)

## Critical Production Gaps (OpenSpec Focus Areas)

🔴 **P0 (Blocking Production):**
1. **Authentication & Authorization** - No user system, all endpoints public
2. **Accessibility (WCAG 2.1 AA)** - Keyboard nav, screen readers, contrast
3. **Comprehensive Testing** - <10% coverage, no E2E tests, no CI/CD

🟡 **P1 (High Priority):**
4. **UI/UX Enhancements** - States overview page, PDF export, URL persistence
5. **Security Hardening** - HTTPS, CORS, CSRF, XSS, input validation
6. **Performance Optimization** - WebSockets (replace polling), caching improvements

See `PRODUCTION_TASKS.md` for detailed task breakdown and `OPENSPEC_FEATURE_DESCRIPTION.md` for comprehensive feature requirements.
