# OpenSpec Feature Description: Nigeria Conflict Tracker Platform

## Feature Name
**Nigeria Conflict Tracker - Production-Ready Enhancement & Security Implementation**

---

## Executive Summary

I want to enhance an **existing conflict tracking platform** that monitors violent conflicts across all 36 Nigerian states using historical and real-time data. The app is already built with advanced ML forecasting, geospatial analysis, and data scraping capabilities, but **needs critical production-ready improvements** in authentication, accessibility, testing, and UI/UX before public launch.

**Current State:** 65% production-ready with strong technical foundation  
**Target State:** 100% production-ready with enterprise-grade security, WCAG 2.1 AA compliance, and comprehensive testing  

---

## Background Context

### What Already Exists
The platform is a **sophisticated full-stack application** with:

**Backend (Python/FastAPI):**
- ✅ 50+ API endpoints for conflicts, forecasts, analytics, geospatial queries
- ✅ PostgreSQL + PostGIS + TimescaleDB database with 10+ tables
- ✅ Machine learning forecasting (Prophet, ARIMA, Ensemble models)
- ✅ Real-time RSS scraping from 15+ Nigerian news sources
- ✅ NLP entity extraction using Groq LLM API
- ✅ Celery task queue for automated scraping & forecasting
- ✅ Redis caching for performance optimization
- ✅ PDF report generation with ReportLab

**Frontend (Next.js/React):**
- ✅ Interactive Mapbox GL JS map with clustering & heat maps
- ✅ Dashboard with time-series charts (Recharts, D3.js)
- ✅ State-level filtering by type, date, fatalities, region
- ✅ ML forecast visualization with confidence intervals
- ✅ ACLED-style conflict index rankings
- ✅ Responsive design with Tailwind CSS + Radix UI

**Infrastructure:**
- ✅ Docker containerization (docker-compose)
- ✅ Railway deployment for backend + PostgreSQL + Redis
- ✅ Vercel deployment for frontend
- ✅ Environment-based configuration

**Data Pipeline:**
- ✅ 774 Nigerian LGAs (Local Government Areas) geocoded
- ✅ Gender-disaggregated casualty tracking
- ✅ Automated deduplication logic
- ✅ Poverty-conflict correlation analysis

### What's Missing (Critical for Production)

🔴 **Security & Authentication:**
- ❌ No user authentication/authorization system
- ❌ No role-based access control (admin, analyst, viewer)
- ❌ No user registration or login functionality
- ❌ All API endpoints are publicly accessible
- ❌ No session management or JWT implementation
- ❌ No audit logging for user actions

🔴 **Accessibility (Legal Compliance):**
- ❌ No WCAG 2.1 AA compliance
- ❌ Limited keyboard navigation
- ❌ No screen reader support
- ❌ Poor color contrast in some areas
- ❌ No ARIA labels or landmarks
- ❌ No accessibility testing (axe-core, Lighthouse)

🔴 **Testing & Quality Assurance:**
- ❌ Minimal unit test coverage (<10%)
- ❌ No end-to-end tests (Cypress)
- ❌ No performance testing (load tests)
- ❌ No CI/CD pipeline (GitHub Actions)
- ❌ No automated quality gates

⚠️ **UI/UX Gaps:**
- ❌ No dedicated "All 36 States" overview page
- ❌ Frontend PDF export not connected to backend
- ❌ Using polling instead of WebSockets for live updates
- ❌ No URL-based filter persistence (can't share filtered views)
- ❌ No saved filter presets
- ❌ Limited mobile optimization (<320px screens)

---

## Target Users

### Primary Users
1. **Security Analysts** - Monitor conflict trends, identify hotspots, generate reports
2. **Researchers** - Analyze historical patterns, export data for academic studies
3. **Government Officials** - Track violence in specific regions, assess risk levels
4. **NGO/Humanitarian Workers** - Plan interventions based on conflict forecasts
5. **Journalists** - Investigate conflict patterns, verify incident data

### User Roles (To Be Implemented)
- **Admin** - Full access: manage users, edit data, configure system
- **Analyst** - Read/write: create reports, export data, view predictions
- **Viewer** - Read-only: view dashboards, maps, basic filtering

---

## Core Features Requiring Enhancement

### 1. Authentication & Authorization System
**Priority:** 🔴 Critical (Blocking Production)

**Requirements:**
- User registration with email verification
- Secure login/logout with JWT tokens (httpOnly cookies)
- Password reset flow (email-based token)
- Role-based access control (admin, analyst, viewer)
- Session management with Redis
- Rate limiting for login attempts (5 per 15 minutes)
- Audit logging for all authentication events
- Protected API endpoints (require valid JWT)
- User profile management (change password, update email)
- Admin dashboard to manage users and roles

**Security Features:**
- HTTPS enforcement in production
- CORS whitelist (frontend domain only)
- CSRF protection for state-changing operations
- XSS protection (input sanitization)
- SQL injection prevention (parameterized queries)
- Security headers (CSP, X-Frame-Options, HSTS)
- Environment variable encryption
- Vulnerability scanning in CI/CD

**Acceptance Criteria:**
- WHEN a user opens the app without authentication, THEN they are redirected to login page
- WHEN a user attempts admin actions without admin role, THEN access is denied with 403 error
- WHEN login fails 5 times, THEN account is temporarily locked for 15 minutes
- WHERE sensitive operations occur, THEN audit logs capture user, action, timestamp

### 2. Accessibility Compliance (WCAG 2.1 AA)
**Priority:** 🔴 Critical (Legal Requirement)

**Keyboard Navigation:**
- Skip-to-content link at page top
- Logical tab order (follows visual flow)
- Visible focus indicators (not color-only)
- Keyboard shortcuts for common actions (/ for search, ? for help)
- Modal dialogs with focus trap (Esc to close)
- Map keyboard controls (arrows to pan, +/- to zoom)
- Dropdown menus navigable with arrow keys

**Screen Reader Support:**
- Semantic HTML (header, nav, main, aside, footer)
- ARIA labels on all icon-only buttons
- ARIA live regions for dynamic content updates
- Proper heading hierarchy (h1 → h2 → h3)
- Visually-hidden text for chart data
- Alt text for all images and map markers
- ARIA landmarks (role="navigation", role="main")

**Visual Accessibility:**
- Color contrast ratio ≥ 4.5:1 for normal text
- Text resize support (up to 200% without layout breaking)
- Dark mode toggle for reduced eye strain
- Focus indicators using outlines/borders (not just color)
- Colorblind-friendly map palette
- Browser zoom support (up to 400% without horizontal scroll)

**Testing:**
- Automated axe-core testing in CI/CD
- Lighthouse accessibility score ≥ 95
- Manual screen reader testing (NVDA, JAWS, VoiceOver)
- Keyboard-only navigation testing

**Acceptance Criteria:**
- WHEN a user presses Tab, THEN focus moves logically through interactive elements
- WHEN screen reader is active, THEN all content is announced correctly
- WHEN page is zoomed to 200%, THEN layout remains functional without horizontal scrolling
- WHERE color is used to convey information, THEN alternative indicators exist

### 3. Comprehensive Testing Suite
**Priority:** 🔴 Critical (Quality Assurance)

**Backend Unit Tests (pytest):**
- Authentication endpoints (register, login, logout)
- Conflict CRUD operations
- ML forecasting models (Prophet, ARIMA)
- NLP extraction pipeline
- Geospatial queries (PostGIS)
- RSS scraping logic
- Target: ≥80% code coverage

**Frontend Unit Tests (Jest + React Testing Library):**
- Authentication components (login, register forms)
- Filter components (state, date, type selectors)
- Map component (Mapbox GL JS)
- Dashboard components
- Chart components (Recharts)
- Target: ≥70% code coverage

**End-to-End Tests (Cypress):**
- User registration → login → dashboard flow
- Filter conflicts by state → view on map
- Export CSV/PDF report
- View ML forecast for state → verify chart renders
- Mobile responsive layout (320px viewport)
- Accessibility tests (axe-core integration)

**Performance Tests (k6):**
- Load test: 1,000 concurrent users on dashboard
- API stress test: 10,000 requests/minute
- Page load time < 2 seconds on 3G
- Database query performance < 500ms
- Redis cache hit rate ≥ 80%

**Data Quality Tests:**
- Geocoding accuracy validation
- NLP extraction precision/recall
- Deduplication effectiveness
- Scraping error handling
- Forecast accuracy metrics (MAE, RMSE)

**CI/CD Pipeline (GitHub Actions):**
- Run all tests on every pull request
- Lint checks (ESLint, Black, isort)
- Security scanning (npm audit, Snyk)
- Accessibility testing (Lighthouse CI)
- Automated deployment to staging on develop branch
- Manual approval for production deployment

**Acceptance Criteria:**
- WHEN code is pushed to GitHub, THEN CI pipeline runs automatically
- WHEN any test fails, THEN pull request is blocked from merging
- WHEN all tests pass, THEN code coverage report is generated
- WHERE performance degrades, THEN alerts are triggered

### 4. UI/UX Enhancements
**Priority:** 🟡 High (User Experience)

**All 36 States Overview Page:**
- Grid/table view showing all Nigerian states
- State statistics cards (total conflicts, fatalities, risk level)
- Sortable/filterable by conflicts, deaths, region
- State comparison feature (select 2-4 states, compare metrics)
- "Data coming soon" placeholder for states with no data
- Click state card → navigate to detailed state page

**Export Functionality:**
- Connect frontend PDF export button to backend PDF generation
- Progress indicator for reports taking >10 seconds
- CSV export with current filter state
- Export dropdown menu (CSV, PDF, Excel options)
- Ability to cancel long-running exports
- Export history page (list of previously generated reports)

**Live Refresh & Real-Time Updates:**
- Replace polling with WebSocket connection
- "Live" indicator badge with last update timestamp
- Auto-pause refresh when user interacts with filters
- Manual refresh button (force immediate fetch)
- Toast notifications for new conflicts ("3 new conflicts in Lagos")
- WebSocket reconnection logic (handle network failures)

**Advanced Filtering:**
- Persist filter state in URL query parameters (?state=Lagos&dateFrom=2024-01-01)
- Shareable filter links (copy URL to share filtered view)
- Saved filter presets (user-defined combinations)
- Filter preset dropdown (load saved filters)
- "Clear All Filters" button
- Filter chips showing active filters (clickable to remove)

**Mobile Responsiveness:**
- Test on 320px - 480px widths
- Touch-friendly map controls (larger tap targets, swipe gestures)
- Collapsible filter drawer on mobile
- Hamburger menu for mobile navigation
- Responsive chart sizing for small screens
- Bottom navigation bar for mobile

**Acceptance Criteria:**
- WHEN user opens States Overview, THEN all 36 states are displayed in a grid
- WHEN export is requested, THEN progress bar shows generation status
- WHEN new conflict is detected, THEN WebSocket pushes update to connected clients
- WHERE filters are applied, THEN URL updates and can be shared
- WHILE user is on mobile, THEN all features remain accessible

---

## Technical Architecture

### Frontend Stack
- **Framework:** Next.js 14+ (React 18+)
- **UI Library:** Radix UI + Tailwind CSS + Shadcn/ui
- **Maps:** Mapbox GL JS
- **Charts:** Recharts, D3.js
- **State Management:** React Context + SWR (for data fetching)
- **Forms:** React Hook Form + Zod validation
- **Testing:** Jest, React Testing Library, Cypress
- **Deployment:** Vercel

### Backend Stack
- **Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL 15+ with PostGIS + TimescaleDB extensions
- **Cache:** Redis 7+
- **Task Queue:** Celery with Redis broker
- **ML:** Prophet, statsmodels (ARIMA), scikit-learn
- **NLP:** Groq LLM API, custom geocoder
- **Scraping:** BeautifulSoup, Feedparser
- **Testing:** pytest, pytest-asyncio, pytest-cov
- **Deployment:** Railway

### Infrastructure
- **Containerization:** Docker + docker-compose
- **CI/CD:** GitHub Actions
- **Monitoring:** (To be added - Sentry, UptimeRobot)
- **Logging:** Structured JSON logging
- **Secrets:** Environment variables (Railway/Vercel)

---

## API Endpoints to Protect

All endpoints under `/api/v1/*` should require JWT authentication except:
- `/api/v1/auth/register` (POST)
- `/api/v1/auth/login` (POST)
- `/api/v1/auth/forgot-password` (POST)
- `/api/v1/auth/reset-password` (POST)
- `/api/v1/health` (GET - for monitoring)

Protected endpoints include:
- `/api/v1/conflicts/*` - Conflict CRUD (admin/analyst write, viewer read)
- `/api/v1/forecasts/*` - ML predictions (all roles read)
- `/api/v1/analytics/*` - Statistical analysis (all roles read)
- `/api/v1/locations/*` - Geographic data (all roles read)
- `/api/v1/exports/*` - Report generation (all roles)
- `/api/v1/admin/*` - User management (admin only)

---

## Non-Functional Requirements

### Performance
- Page load time: < 2 seconds on 3G connection
- API response time: < 500ms for 95th percentile
- Support 1,000 concurrent users
- Database queries: < 500ms for complex queries
- Map tile loading: < 1 second

### Security
- HTTPS-only in production
- JWT tokens expire after 1 hour (refresh tokens valid 7 days)
- Password minimum: 8 characters, 1 uppercase, 1 number, 1 special char
- Rate limiting: 100 requests/minute per user
- Session timeout: 30 minutes of inactivity
- OWASP Top 10 compliance

### Reliability
- 99.9% uptime during business hours (08:00-20:00 WAT)
- Automated database backups (daily to S3/cloud storage)
- Graceful degradation (map works without real-time data)
- Error recovery (automatic retry for failed scrapers)

### Scalability
- Horizontal scaling for backend (stateless services)
- Database read replicas for heavy queries
- CDN for static assets (Vercel Edge Network)
- Redis cluster for high-traffic caching

### Accessibility
- WCAG 2.1 AA compliance (all pages)
- Lighthouse accessibility score ≥ 95
- Keyboard navigation for all features
- Screen reader compatible (NVDA, JAWS, VoiceOver)
- Minimum color contrast 4.5:1

### Browser Support
- Chrome/Edge 90+
- Firefox 90+
- Safari 14+
- Mobile Safari iOS 14+
- Chrome Android 90+

---

## Data Model Overview

**Existing Tables:**
- `conflicts` - Main events table (TimescaleDB hypertable)
- `states` - 36 Nigerian states with geospatial boundaries
- `lgas` - 774 Local Government Areas
- `communities` - ~10,000 villages/communities
- `forecasts` - ML predictions by state
- `actors` - Armed groups database
- `news_articles` - Scraped articles with NER linkage
- `social_chatter` - Social media monitoring (TimescaleDB)
- `poverty_indicators` - Economic correlation data

**New Tables Needed:**
- `users` - User accounts (id, email, hashed_password, role, created_at, last_login)
- `roles` - Role definitions (id, name, permissions)
- `sessions` - Active user sessions (Redis-backed)
- `audit_log` - User action tracking (user_id, action, resource, timestamp, details)
- `exports` - Generated reports history (user_id, type, filters, generated_at, file_url)
- `filter_presets` - Saved user filters (user_id, name, filter_config, is_public)

---

## Success Metrics

### Security Metrics
- ✅ 100% of API endpoints protected by authentication
- ✅ 0 critical security vulnerabilities (Snyk scan)
- ✅ All passwords hashed with bcrypt (cost factor ≥12)
- ✅ HTTPS enforced (HTTP redirects to HTTPS)

### Accessibility Metrics
- ✅ Lighthouse accessibility score ≥ 95 (all pages)
- ✅ 0 critical axe-core violations
- ✅ All interactive elements keyboard-accessible
- ✅ WCAG 2.1 AA compliance report generated

### Testing Metrics
- ✅ Backend code coverage ≥ 80%
- ✅ Frontend code coverage ≥ 70%
- ✅ All E2E tests passing (≥15 Cypress scenarios)
- ✅ Performance tests pass (1,000 concurrent users)

### User Experience Metrics
- ✅ Page load time < 2s on 3G
- ✅ Time to interactive < 3s
- ✅ Map rendering < 1s
- ✅ Mobile usability score ≥ 90 (Lighthouse)

### Production Readiness
- ✅ CI/CD pipeline operational (GitHub Actions)
- ✅ Automated backups configured
- ✅ Monitoring & alerting active
- ✅ Documentation complete (API docs, user guide, developer guide)

---

## Out of Scope (Existing Features to Keep)

The following features are **already implemented and working well** - do not modify:
- ✅ Machine learning forecasting (Prophet, ARIMA, Ensemble)
- ✅ RSS news scraping from 15+ Nigerian sources
- ✅ NLP entity extraction with Groq LLM
- ✅ Geospatial analysis (PostGIS queries, hotspot detection)
- ✅ TimescaleDB time-series optimization
- ✅ Mapbox GL JS map implementation
- ✅ Dashboard charts and visualizations
- ✅ ACLED-style conflict index
- ✅ Gender-disaggregated casualty tracking
- ✅ Celery automated task scheduling
- ✅ Redis caching layer
- ✅ Docker containerization
- ✅ Railway + Vercel deployment configurations

---

## Deliverables Expected

1. **Comprehensive requirements document (EARS format)** with:
   - User stories for authentication, accessibility, testing, UI/UX
   - Acceptance criteria using WHEN/IF/THEN/WHERE
   - Non-functional requirements (performance, security, reliability)

2. **Technical design document** with:
   - Authentication architecture (JWT flow diagrams)
   - Database schema changes (users, roles, audit_log tables)
   - API endpoint specifications (protected routes)
   - Accessibility implementation approach
   - Testing strategy (unit, E2E, performance)
   - CI/CD pipeline architecture

3. **Detailed task breakdown** with:
   - Granular tasks for each phase (auth, accessibility, testing, UI/UX)
   - Time estimates per task
   - Dependencies between tasks
   - Agent routing (which specialized agent handles each task)
   - Sprint planning (2-week sprints)
   - Critical path to production

4. **Architecture diagrams** (Mermaid format):
   - Authentication flow (login, JWT refresh, role checks)
   - CI/CD pipeline (GitHub Actions workflow)
   - Testing pyramid (unit → integration → E2E)
   - Deployment architecture (frontend, backend, databases)

---

## Special Considerations

### Nigerian Context
- Platform focuses on **organized violence** (armed groups, insurgencies, communal clashes), not individual crimes
- Geographic coverage: All 36 states + FCT (Federal Capital Territory)
- Supports 774 Local Government Areas with precise geocoding
- Data sources are Nigerian news outlets and conflict databases
- User base includes government agencies, NGOs, researchers

### Data Privacy
- Conflict data is **public information** (news-based)
- User authentication required to prevent abuse
- Audit logging for accountability
- No PII (Personally Identifiable Information) collected beyond email

### Performance Constraints
- Large datasets (10,000+ conflict records)
- Real-time map rendering with clustering
- ML model inference can be compute-intensive
- Must work on low-bandwidth connections (3G)

### Compliance Requirements
- WCAG 2.1 AA (accessibility law in many countries)
- GDPR considerations for user data (if EU users)
- Nigerian Data Protection Regulation (NDPR) compliance

---

## Timeline Expectations

**Ideal Timeline:** 16-20 weeks (4-5 months) with a full development team

**Critical Path:**
1. **Weeks 1-2:** Authentication backend + frontend
2. **Weeks 2-3:** Security hardening
3. **Weeks 3-5:** Accessibility implementation
4. **Weeks 5-7:** Comprehensive testing
5. **Weeks 7-8:** CI/CD + production deployment
6. **Weeks 8-10:** UI/UX enhancements
7. **Weeks 10-12:** Documentation + handoff
8. **Weeks 12-16:** Buffer for issues, final QA

**Team Size:** 2-3 developers, 1 QA engineer, 1 DevOps engineer

---

## References

- **Current App URL:** https://naija-conflict-tracker.vercel.app/
- **GitHub Repo:** (private)
- **Tech Stack:** Python/FastAPI backend, Next.js frontend, PostgreSQL+PostGIS
- **Deployment:** Railway (backend), Vercel (frontend)
- **WCAG 2.1 AA Guidelines:** https://www.w3.org/WAI/WCAG21/quickref/
- **OWASP Top 10:** https://owasp.org/www-project-top-ten/

---

## Questions for Clarification (Optional)

1. **User Registration:** Should users self-register, or admin-only user creation?
2. **Email Service:** Which email provider for password resets? (SendGrid, AWS SES, etc.)
3. **Monitoring:** Preference for monitoring tools? (Sentry, Datadog, custom)
4. **Social Login:** Support OAuth (Google, Microsoft) for authentication?
5. **Data Export Limits:** Max rows for CSV export? (performance consideration)
6. **Accessibility Exceptions:** Any known WCAG exemptions? (e.g., maps are partially exempt)

---

**This feature description is optimized for OpenSpec to generate production-ready specifications for authentication, accessibility, testing, and UI/UX enhancements to an existing conflict tracking platform.**
