# UI/Frontend Wireframe Implementation Tasks

**Status:** In Progress  
**Started:** 2026-01-27  
**Priority:** High

## Overview
Implement comprehensive UI wireframes based on proposal.md, leveraging existing Next.js Pages Router frontend with TypeScript, Tailwind CSS, and component libraries already in place.

---

## Pre-Implementation Discovery

- [x] 0.1 Activate Serena project tools
- [x] 0.2 Analyze existing frontend structure
- [x] 0.3 Identify reusable components (StatsCard, TrendChart, ConflictMap, etc.)
- [ ] 0.4 Audit current page routing structure
- [ ] 0.5 Review existing API integration patterns
- [ ] 0.6 Assess authentication/authorization implementation

---

## Phase 1: Foundation & Design System (Week 1)

### 1.1 Design System Setup
- [ ] 1.1.1 Create design tokens file (colors, typography, spacing)
- [ ] 1.1.2 Extend Tailwind config with Nigeria-themed palette
- [ ] 1.1.3 Document component usage guidelines
- [ ] 1.1.4 Create Storybook setup for component preview (optional)

### 1.2 Layout Components
- [ ] 1.2.1 Enhance DashboardLayout with role-based sidebar
- [ ] 1.2.2 Create collapsible navigation with icons
- [ ] 1.2.3 Build top bar with notifications and user menu
- [ ] 1.2.4 Implement mobile responsive drawer
- [ ] 1.2.5 Add active route highlighting

### 1.3 Shared UI Components
- [ ] 1.3.1 Create FilterPanel component (date range, state/LGA, event type)
- [ ] 1.3.2 Build DetailPanel component (incident details, slides from right)
- [ ] 1.3.3 Enhance existing Card components with loading states
- [ ] 1.3.4 Create EmptyState component
- [ ] 1.3.5 Build ErrorBoundary component

**Agent Assignments:**
- **DATAVIZ_AGENT**: Design system tokens, component guidelines
- **API_AGENT**: Review existing API integration patterns

---

## Phase 2: Public Pages (Week 2)

### 2.1 Landing Page (/)
- [ ] 2.1.1 Create hero section with value proposition
- [ ] 2.1.2 Build live statistics cards (via `/api/v1/public/landing-stats`)
- [ ] 2.1.3 Add interactive map preview (Mapbox GL JS)
- [ ] 2.1.4 Implement recent incidents feed (limited to 5)
- [ ] 2.1.5 Create feature highlights section
- [ ] 2.1.6 Add CTAs (Get Started, View Demo)

### 2.2 About & Methodology Pages
- [ ] 2.2.1 Create /about page with mission, vision
- [ ] 2.2.2 Build /methodology page explaining data sources, models
- [ ] 2.2.3 Add team section (optional)

**Agent Assignments:**
- **CARTOGRAPHY_AGENT**: Map preview on landing page
- **DATAVIZ_AGENT**: Statistics cards visualization

---

## Phase 3: Authentication Pages (Week 2)

### 3.1 Login Page (/login)
- [ ] 3.1.1 Build login form with email/password
- [ ] 3.1.2 Add password visibility toggle
- [ ] 3.1.3 Implement "Remember me" checkbox
- [ ] 3.1.4 Add error handling (invalid credentials, rate limiting)
- [ ] 3.1.5 Integrate with `POST /api/v1/auth/login`
- [ ] 3.1.6 Handle JWT token storage
- [ ] 3.1.7 Redirect to /dashboard on success

### 3.2 Register Page (/register)
- [ ] 3.2.1 Build registration form (email, password, full name)
- [ ] 3.2.2 Add real-time password strength indicator
- [ ] 3.2.3 Implement email uniqueness validation
- [ ] 3.2.4 Add password confirmation matching
- [ ] 3.2.5 Add terms acceptance checkbox
- [ ] 3.2.6 Integrate with `POST /api/v1/auth/register`
- [ ] 3.2.7 Auto-assign "viewer" role on success

### 3.3 Forgot Password (/forgot-password)
- [ ] 3.3.1 Create forgot password form
- [ ] 3.3.2 Integrate with password reset flow
- [ ] 3.3.3 Add success/error feedback

**Agent Assignments:**
- **API_AGENT**: Authentication integration, JWT handling

---

## Phase 4: Dashboard Overview (Week 3)

### 4.1 Dashboard Overview Page (/dashboard)
- [ ] 4.1.1 Enhance existing dashboard with wireframe layout
- [ ] 4.1.2 Add KPI cards with trend indicators (↑12%, ↓8%)
- [ ] 4.1.3 Integrate time-series chart (last 6 months)
- [ ] 4.1.4 Create top hotspots list component
- [ ] 4.1.5 Build recent incidents feed
- [ ] 4.1.6 Add quick action buttons
- [ ] 4.1.7 Fetch data from:
  - `GET /api/v1/analytics/dashboard-summary`
  - `GET /api/v1/analytics/trends?period=monthly&months=6`
  - `GET /api/v1/analytics/hotspots?limit=5`
  - `GET /api/v1/conflicts?limit=10`

**Agent Assignments:**
- **DATAVIZ_AGENT**: KPI cards, trend chart, visualization components
- **API_AGENT**: Dashboard API integration

---

## Phase 5: Interactive Map Page (Week 4)

### 5.1 Map Page (/map)
- [ ] 5.1.1 Create full-page map layout
- [ ] 5.1.2 Integrate Mapbox GL JS (enhance existing ConflictMap)
- [ ] 5.1.3 Add cluster markers for nearby incidents
- [ ] 5.1.4 Implement heat map overlay
- [ ] 5.1.5 Add state/LGA boundary overlays
- [ ] 5.1.6 Create zoom controls
- [ ] 5.1.7 Add geolocation button
- [ ] 5.1.8 Implement search/geocoding

### 5.2 Filter Panel (Sidebar)
- [ ] 5.2.1 Build sticky filter panel
- [ ] 5.2.2 Add collapsible functionality on mobile
- [ ] 5.2.3 Create multi-select dropdowns (states, event types)
- [ ] 5.2.4 Add date range picker (preset + custom)
- [ ] 5.2.5 Implement casualty threshold slider
- [ ] 5.2.6 Add real-time filter application
- [ ] 5.2.7 Show filter count badges
- [ ] 5.2.8 Add reset functionality

### 5.3 Detail Panel
- [ ] 5.3.1 Build slide-in panel from right
- [ ] 5.3.2 Display incident metadata on marker click
- [ ] 5.3.3 Show actor information
- [ ] 5.3.4 Add verification status badge
- [ ] 5.3.5 Display source attribution
- [ ] 5.3.6 Link to full incident detail

### 5.4 Performance Optimizations
- [ ] 5.4.1 Implement marker clustering for large datasets
- [ ] 5.4.2 Add lazy loading of incident details
- [ ] 5.4.3 Debounce filter updates
- [ ] 5.4.4 Use viewport-based queries

**Agent Assignments:**
- **CARTOGRAPHY_AGENT**: Map implementation, clustering, heat maps, styling
- **GEOSPATIAL_AGENT**: Spatial queries, geocoding integration
- **API_AGENT**: Conflict data API integration

---

## Phase 6: Analytics Dashboards (Week 5-6)

### 6.1 Hotspots Page (/analytics/hotspots)
- [ ] 6.1.1 Create control panel (timeframe, parameters)
- [ ] 6.1.2 Build heat map visualization
- [ ] 6.1.3 Create sortable data table with risk levels
- [ ] 6.1.4 Implement color-coded risk indicators
- [ ] 6.1.5 Add drill-down (state → LGA)
- [ ] 6.1.6 Add export functionality (CSV, PDF)
- [ ] 6.1.7 Integrate with `GET /api/v1/analytics/hotspots`

### 6.2 Trends Page (/analytics/trends)
- [ ] 6.2.1 Build time-series charts
- [ ] 6.2.2 Add period selector (daily/weekly/monthly)
- [ ] 6.2.3 Create state comparison view
- [ ] 6.2.4 Add export options
- [ ] 6.2.5 Integrate with `GET /api/v1/analytics/trends`

### 6.3 Correlations Page (/analytics/correlations)
- [ ] 6.3.1 Create poverty-conflict scatter plots
- [ ] 6.3.2 Display statistical significance
- [ ] 6.3.3 Add interactive filters
- [ ] 6.3.4 Integrate with correlation API

### 6.4 Archetypes Page (/analytics/archetypes)
- [ ] 6.4.1 Build conflict type breakdown charts
- [ ] 6.4.2 Create actor analysis visualization
- [ ] 6.4.3 Add pattern recognition display
- [ ] 6.4.4 Integrate with archetype API

**Agent Assignments:**
- **DATAVIZ_AGENT**: All chart components, visualizations
- **STATISTICIAN_AGENT**: Correlation visualizations, significance displays
- **API_AGENT**: Analytics API integration

---

## Phase 7: Forecasting Dashboard (Week 7)

### 7.1 Forecasts Page (/forecasts) - Analyst+ Role
- [ ] 7.1.1 Create configuration panel
  - [ ] Location type selector (State/LGA)
  - [ ] Location picker dropdown
  - [ ] Model selector (Ensemble/Prophet/ARIMA)
  - [ ] Forecast horizon slider (1-12 weeks)
- [ ] 7.1.2 Build forecast visualization chart
  - [ ] Historical vs predicted line chart
  - [ ] 95% confidence interval shading
  - [ ] Legend with color coding
- [ ] 7.1.3 Create prediction cards (next week, 2 weeks, 4 weeks)
- [ ] 7.1.4 Display model performance metrics
  - [ ] MAE, RMSE, MAPE
  - [ ] Training data info
  - [ ] Last updated timestamp
- [ ] 7.1.5 Add forecast data export
- [ ] 7.1.6 Integrate with:
  - `POST /api/v1/forecasts/prophet`
  - `POST /api/v1/forecasts/arima`
  - `POST /api/v1/forecasts/ensemble`

**Agent Assignments:**
- **DATA_SCIENCE_AGENT**: Model selector logic, performance metrics
- **DATAVIZ_AGENT**: Forecast charts, confidence intervals
- **API_AGENT**: Forecast API integration

---

## Phase 8: Incidents Management (Week 8)

### 8.1 Incidents Table Page (/incidents)
- [ ] 8.1.1 Create data table with advanced filters
- [ ] 8.1.2 Add pagination controls
- [ ] 8.1.3 Implement sorting on columns
- [ ] 8.1.4 Build detail view modal
- [ ] 8.1.5 Add export (CSV/Excel)
- [ ] 8.1.6 Add "Create New" button (Analyst+ only)
- [ ] 8.1.7 Integrate with `GET /api/v1/conflicts`

### 8.2 Incident Detail Modal
- [ ] 8.2.1 Display full incident information
- [ ] 8.2.2 Show related incidents
- [ ] 8.2.3 Display source links
- [ ] 8.2.4 Add edit button (Analyst+)

**Agent Assignments:**
- **API_AGENT**: CRUD operations, pagination
- **DATAVIZ_AGENT**: Table component, filtering UI

---

## Phase 9: Reports & Monitoring (Week 9)

### 9.1 Reports Page (/reports)
- [ ] 9.1.1 List pre-generated reports
- [ ] 9.1.2 Build custom report builder (Analyst+)
- [ ] 9.1.3 Add PDF download functionality
- [ ] 9.1.4 Create scheduled reports UI (Analyst+)

### 9.2 Monitoring Dashboard (/monitoring) - Admin Only
- [ ] 9.2.1 Create pipeline health dashboard
- [ ] 9.2.2 Display data quality metrics
- [ ] 9.2.3 Show system resource usage
- [ ] 9.2.4 Build scraping status panel
- [ ] 9.2.5 Display worker health
- [ ] 9.2.6 Add manual trigger controls
- [ ] 9.2.7 Integrate with `GET /api/v1/monitoring/*`

**Agent Assignments:**
- **REPORT_GENERATOR_AGENT**: Report generation logic
- **INFRA_AGENT**: Monitoring dashboard, system metrics
- **API_AGENT**: Monitoring API integration

---

## Phase 10: Admin & Profile (Week 10)

### 10.1 Admin Page (/admin) - Admin Only
- [ ] 10.1.1 Create user management table
- [ ] 10.1.2 Build role assignment UI
- [ ] 10.1.3 Display audit logs
- [ ] 10.1.4 Add system settings panel

### 10.2 Profile Page (/profile)
- [ ] 10.2.1 Display personal information
- [ ] 10.2.2 Add change password form
- [ ] 10.2.3 Create session management UI
- [ ] 10.2.4 Add API token generation (Analyst+)

**Agent Assignments:**
- **API_AGENT**: User management, profile APIs

---

## Phase 11: Polish & Optimization (Week 10)

### 11.1 Accessibility (WCAG 2.1 AA)
- [ ] 11.1.1 Add keyboard navigation support
- [ ] 11.1.2 Implement screen reader labels (aria-*)
- [ ] 11.1.3 Ensure color contrast ratios
- [ ] 11.1.4 Add focus indicators
- [ ] 11.1.5 Test with screen readers

### 11.2 Performance Optimization
- [ ] 11.2.1 Implement code splitting (Next.js dynamic imports)
- [ ] 11.2.2 Add image optimization (next/image)
- [ ] 11.2.3 Setup caching strategies (SWR)
- [ ] 11.2.4 Optimize bundle size
- [ ] 11.2.5 Add loading skeletons

### 11.3 Security
- [ ] 11.3.1 Implement XSS protection
- [ ] 11.3.2 Add CSRF token validation
- [ ] 11.3.3 Secure API calls (httpOnly cookies)
- [ ] 11.3.4 Add rate limiting on frontend
- [ ] 11.3.5 Implement content security policy

### 11.4 Testing
- [ ] 11.4.1 Write unit tests for components
- [ ] 11.4.2 Add integration tests for pages
- [ ] 11.4.3 Create E2E tests (Playwright/Cypress)
- [ ] 11.4.4 Test role-based access

**Agent Assignments:**
- **QUALITY_ASSURANCE_AGENT**: Testing, accessibility audits
- **INFRA_AGENT**: Performance monitoring, optimization

---

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Build succeeds without errors
- [ ] All pages render correctly
- [ ] Authentication flow works
- [ ] Role-based access enforced
- [ ] API integration verified
- [ ] Mobile responsiveness tested
- [ ] Accessibility compliance verified
- [ ] Performance benchmarks met (<2s page load)

---

## Success Criteria

**Functional:**
- ✅ All 15+ pages implemented per wireframes
- ✅ Role-based access control enforced
- ✅ Real-time data integration
- ✅ Map visualization with clustering
- ✅ Forecasting dashboard functional

**Technical:**
- ✅ TypeScript with no critical errors
- ✅ Tailwind CSS for styling
- ✅ Responsive (mobile, tablet, desktop)
- ✅ Accessibility (WCAG 2.1 AA)
- ✅ Performance (<2s page load, <500ms API)

**User Experience:**
- ✅ Intuitive navigation
- ✅ Consistent design language
- ✅ Clear data visualizations
- ✅ Helpful error messages
- ✅ Loading states for async operations

---

## Notes
- Leverage existing components where possible (StatsCard, TrendChart, ConflictMap)
- Use @tanstack/react-query for data fetching (already installed)
- Utilize existing Radix UI components
- Follow existing TypeScript patterns
- Maintain consistency with current styling approach
