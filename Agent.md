# Agent Documentation - Nigeria Conflict Tracker

## Agent Overview

This AI agent specializes in the Nigeria Conflict Tracker project, a real-time conflict monitoring and predictive analytics platform tracking violent conflicts across Nigeria's 36 states.

## Project Context

### Technology Stack
- **Backend**: FastAPI (Python), PostgreSQL + PostGIS, Redis, Celery
- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Maps**: Leaflet + OpenStreetMap (free alternative to Mapbox)
- **Charts**: Recharts, D3.js
- **Deployment**: Vercel (frontend), Railway (backend)

### Key Features
- Real-time conflict tracking across Nigeria
- AI-powered forecasting with Prophet/ARIMA models
- Geospatial analysis with PostGIS
- WebSocket real-time updates
- Role-based authentication (Viewer/Analyst/Admin)
- ACLED-level spatial analysis capabilities

### Database Structure
- **Primary Table**: `conflicts` (5,998 records - matches original MySQL schema from `u503102722_conflictdb (1).sql`)
- **Dashboard View**: `conflict_events` (6,993 records - denormalized for UI performance)
- **Supporting Tables**: `alert_events`, `actors`, `conflict_types`, `states`, `lgas`

## Current Issues & Fixes

### Critical Issue: Dashboard Data Disconnect
**Status**: OpenSpec change created, ready for implementation

**Problem**: Dashboard shows "0 Events awaiting verification" when database contains 6,982 unverified events.

**Files Involved**:
- `backend/app/api/v1/endpoints/monitoring.py` - API endpoints
- `frontend/components/dashboard/PerformanceDashboard.tsx` - Dashboard UI
- `frontend/contexts/AuthContext.tsx` - Authentication

**OpenSpec Change**: `fix-dashboard-api-connectivity`
- All 4 artifacts complete (proposal, design, specs, tasks)
- 47 implementation tasks ready
- Handoff document created

### Previous Fixes Implemented
- **Authentication System**: JWT token validation, automatic refresh, CORS configuration
- **Data Validation**: Enhanced MonthlyTrendsChart validation, error handling
- **Build Issues**: Fixed import paths, resolved Leaflet SSR issues
- **Deployment**: Configured Railway backend, Vercel frontend

## Agent Capabilities

### Database Operations
- Direct PostgreSQL database access via psql
- Query execution and validation
- Schema analysis and optimization
- Data migration and validation

### Code Analysis & Development
- Full-stack development (Python FastAPI + Next.js)
- Database schema design and optimization
- API endpoint development and debugging
- Frontend component development with TypeScript
- Authentication and authorization systems

### OpenSpec Workflow Management
- Create and manage changes using spec-driven workflow
- Generate proposals, designs, specs, and implementation tasks
- Track progress and maintain documentation
- Handoff creation for continuity

### DevOps & Deployment
- Railway backend deployment
- Vercel frontend deployment
- Environment configuration
- Performance monitoring and debugging

## Project Architecture

### Backend Structure
```
backend/
├── app/
│   ├── api/v1/
│   │   ├── endpoints/monitoring.py    # Dashboard data APIs
│   │   └── api.py                     # Router configuration
│   ├── core/                          # Core functionality
│   ├── models/                        # Database models
│   └── tasks/                         # Background tasks
├── alembic/                          # Database migrations
└── config/                           # Configuration files
```

### Frontend Structure
```
frontend/
├── components/
│   ├── dashboard/                     # Dashboard components
│   ├── admin/                        # Admin interface
│   └── analytics/                    # Analytics components
├── contexts/                         # React contexts
├── hooks/                           # Custom hooks
└── __tests__/                        # Test files
```

## Database Connection Information

**Production Database**: PostgreSQL on Neon
**Connection**: `postgresql://neondb_owner:npg_bL6dDyw8WEMI@ep-gentle-union-agwmnyzn-pooler.c-2.eu-central-1.aws.neon.tech/neondb`

**Key Views**:
- `conflict_events` - Dashboard data (6,993 records)
- `conflicts` - Original data (5,998 records)

## Authentication Context

**Production Login**: info@thenextier.com / test12345
**Dashboard URL**: https://naija-conflict-tracker.vercel.app/dashboard
**Access Level**: Full verification system

## Development Workflow

### OpenSpec Integration
- Use `openspec new change <name>` to start new features
- Follow spec-driven workflow: proposal → design → specs → tasks
- Use `openspec apply-change` for implementation
- Archive completed changes with `openspec archive-change`

### Testing Strategy
- Test all database queries directly via psql
- Validate API endpoints locally before deployment
- Use provided authentication credentials for testing
- Compare UI data with database reality

### Deployment Process
1. Test locally with real database
2. Deploy backend to Railway
3. Deploy frontend to Vercel
4. Verify production functionality
5. Monitor logs and performance

## Common Issues & Solutions

### Dashboard Showing Zero Values
**Cause**: API connectivity issues, authentication blocks, or database connection failures
**Solution**: Check monitoring endpoints, verify database connectivity, test authentication flow

### Build Errors
**Cause**: Import path issues, SSR problems with Leaflet
**Solution**: Update import paths, use dynamic imports for client-side components

### Authentication Issues
**Cause**: JWT token validation, CORS configuration
**Solution**: Enhanced token validation, automatic refresh, proper CORS setup

## Agent Specializations

### Senior Principal Engineer (Frontend)
- React/Next.js development with TypeScript
- Component architecture and state management
- Performance optimization and error handling
- UI/UX implementation with Tailwind CSS

### Backend Development
- FastAPI endpoint development and debugging
- PostgreSQL database operations and optimization
- Authentication and authorization systems
- Background task processing with Celery

### Data Analysis
- Conflict data validation and migration
- Geospatial analysis with PostGIS
- Real-time data pipeline development
- AI/ML integration for conflict forecasting

## Contact & Continuity

**Project Repository**: Nigeria Conflict Tracker
**Critical Issues**: Dashboard data disconnect (immediate resolution required)
**Documentation**: Agent.md, handoff documents, OpenSpec changes
**Deployment**: Railway (backend), Vercel (frontend)

---

**Last Updated**: Feb 10, 2026  
**Active Issues**: Dashboard API connectivity fix (OpenSpec ready)  
**Agent Focus**: Full-stack development with database expertise
