# UI/Frontend Wireframe Implementation - Discovery Report

**Date:** 2026-01-27  
**Status:** Discovery Complete  
**Next:** Begin Phase 1 Implementation

---

## Executive Summary

The Nextier Nigeria Conflict Tracker frontend has a **strong foundation** with 70+ existing components, robust authentication, React Query integration, and Mapbox GL JS setup. The wireframe implementation will **enhance and reorganize** existing components rather than build from scratch.

**Recommendation:** Proceed with **incremental enhancement** approach, focusing on:
1. Layout reorganization (sidebar navigation)
2. Page routing cleanup (align with wireframes)
3. Component composition (assemble existing pieces)
4. Role-based UI refinement
5. Polish and accessibility improvements

---

## Current Frontend Architecture

### Technology Stack ✅
- **Framework:** Next.js 14 (Pages Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** React Query + Context API
- **Authentication:** JWT with localStorage
- **Maps:** Mapbox GL JS + Leaflet
- **Charts:** Recharts + D3.js
- **UI Components:** Radix UI + shadcn/ui

### Project Structure
```
frontend/
├── pages/
│   ├── index.tsx                # Landing page ✅
│   ├── login.tsx                # Login ✅
│   ├── register.tsx             # Register ✅
│   ├── analytics.tsx            # Analytics page
│   ├── forecasts.tsx            # Forecasts page
│   ├── map.tsx                  # Map page
│   ├── conflict-index.tsx       # Conflict index
│   ├── unauthorized.tsx         # 401 page
│   └── dashboard/
│       └── index.tsx            # Dashboard overview ✅
│
├── components/
│   ├── landing/                 # Landing page components ✅
│   │   ├── LandingPage.tsx
│   │   ├── StatCard.tsx
│   │   ├── NigeriaMap.tsx
│   │   └── ...
│   ├── dashboard/               # Dashboard components ✅
│   │   ├── ConflictDashboard.tsx
│   │   ├── StatsCard.tsx
│   │   ├── TrendChart.tsx
│   │   ├── RecentIncidents.tsx
│   │   └── ...
│   ├── maps/                    # Map components ✅
│   │   └── ConflictMap.tsx
│   ├── charts/                  # Chart components ✅
│   │   ├── TrendsChart.tsx
│   │   ├── MonthlyTrendsChart.tsx
│   │   └── ...
│   ├── layouts/                 # Layout components
│   │   ├── DashboardLayout.tsx  # Needs enhancement
│   │   └── ProfessionalLayout.tsx
│   ├── ui/                      # Base UI components ✅
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── badge.tsx
│   │   └── tabs.tsx
│   └── ...
│
├── contexts/
│   └── AuthContext.tsx          # Authentication state ✅
│
├── hooks/                       # Custom React hooks
├── lib/
│   ├── auth-api.ts              # Auth API client ✅
│   └── map/                     # Map utilities ✅
│
└── styles/
    ├── globals.css
    └── map.css
```

---

## What's Already Built ✅

### Authentication System (90% Complete)
- ✅ JWT authentication with access/refresh tokens
- ✅ Role-based access control (admin/analyst/viewer)
- ✅ `AuthContext` with login/logout/register
- ✅ `ProtectedRoute` component
- ✅ Token storage in localStorage
- ✅ Auto token refresh
- ⚠️  **Gap:** Password reset flow (forgot-password page missing)
- ⚠️  **Gap:** httpOnly cookies (currently using localStorage)

### Landing Page (80% Complete)
- ✅ `LandingPage` component with hero
- ✅ `StatCard` component for metrics
- ✅ `NigeriaMap` component for map preview
- ✅ `ArchetypeChart` and `EconomicPulseChart`
- ⚠️  **Gap:** Recent incidents feed
- ⚠️  **Gap:** Call-to-action buttons
- ⚠️  **Gap:** Feature highlights section

### Dashboard Components (70% Complete)
- ✅ `ConflictDashboard` with KPIs
- ✅ `StatsCard` for metrics display
- ✅ `TrendChart` for time-series
- ✅ `RecentIncidents` feed
- ✅ `ProfessionalLayout` for dashboard wrapper
- ⚠️  **Gap:** Sidebar navigation (currently top nav)
- ⚠️  **Gap:** User menu dropdown
- ⚠️  **Gap:** Notifications bell

### Map Components (60% Complete)
- ✅ `ConflictMap` with Mapbox GL JS
- ✅ `AdvancedConflictMap` with advanced features
- ✅ Map utilities (clustering, colors)
- ⚠️  **Gap:** Filter panel sidebar
- ⚠️  **Gap:** Detail panel (incident popup)
- ⚠️  **Gap:** Heat map overlay toggle
- ⚠️  **Gap:** Layer controls

### Analytics (50% Complete)
- ✅ Analytics page exists
- ✅ Chart components (TrendsChart, MonthlyTrendsChart, StateComparisonChart)
- ⚠️  **Gap:** Hotspots page
- ⚠️  **Gap:** Correlations page
- ⚠️  **Gap:** Archetypes page

### Forecasting (40% Complete)
- ✅ Forecasts page exists
- ⚠️  **Gap:** Model selector UI
- ⚠️  **Gap:** Location picker
- ⚠️  **Gap:** Forecast horizon slider
- ⚠️  **Gap:** Confidence interval chart

### UI Components (90% Complete)
- ✅ Radix UI primitives (button, card, badge, tabs)
- ✅ Tailwind CSS configured
- ✅ Heroicons for icons
- ⚠️  **Gap:** FilterPanel component
- ⚠️  **Gap:** DetailPanel component
- ⚠️  **Gap:** EmptyState component

---

## Implementation Gaps (What Needs Building)

### High Priority
1. **Sidebar Navigation** - Replace top nav with collapsible sidebar
2. **Role-Based Menus** - Show/hide menu items based on user role
3. **Filter Panel** - Reusable filter component for map/analytics
4. **Detail Panel** - Slide-in panel for incident details
5. **Forgot Password Flow** - Complete password reset
6. **Page Routing Alignment** - Match wireframe structure

### Medium Priority
7. **User Menu Dropdown** - Profile, settings, logout
8. **Notifications Bell** - System alerts
9. **Hotspots Page** - `/dashboard/analytics/hotspots`
10. **Correlations Page** - `/dashboard/analytics/correlations`
11. **Archetypes Page** - `/dashboard/analytics/archetypes`
12. **Incidents Table Page** - `/dashboard/incidents`
13. **Reports Page** - `/dashboard/reports`

### Low Priority
14. **Monitoring Dashboard** - Admin-only system monitoring
15. **Admin Panel** - User management
16. **Profile Page** - User profile settings
17. **About/Methodology Pages** - Static content

---

## Recommended Implementation Plan

### Phase 1: Layout Reorganization (Week 1) - **DATAVIZ_AGENT**
**Goal:** Transform horizontal nav to sidebar layout per wireframes

**Tasks:**
1. Create `Sidebar.tsx` component with collapsible navigation
2. Add role-based menu item filtering
3. Build `TopBar.tsx` with notifications + user menu
4. Update `DashboardLayout.tsx` to use sidebar
5. Add mobile responsive drawer
6. Update all pages to use new layout

**Files to modify:**
- `components/layouts/DashboardLayout.tsx`
- Create: `components/layouts/Sidebar.tsx`
- Create: `components/layouts/TopBar.tsx`
- Create: `components/layouts/UserMenu.tsx`

**Estimated Time:** 2-3 days

---

### Phase 2: Shared Components (Week 1-2) - **DATAVIZ_AGENT**
**Goal:** Build reusable UI components from wireframes

**Tasks:**
1. Create `FilterPanel.tsx` - Date range, state/LGA, event type filters
2. Create `DetailPanel.tsx` - Slide-in panel for incident details
3. Create `EmptyState.tsx` - Empty data state
4. Create `LoadingSkeleton.tsx` - Loading placeholders
5. Enhance existing components with loading states

**Files to create:**
- `components/shared/FilterPanel.tsx`
- `components/shared/DetailPanel.tsx`
- `components/shared/EmptyState.tsx`
- `components/shared/LoadingSkeleton.tsx`

**Estimated Time:** 2-3 days

---

### Phase 3: Map Page Enhancement (Week 2) - **CARTOGRAPHY_AGENT**
**Goal:** Implement interactive map page per wireframes

**Tasks:**
1. Create `/dashboard/map` page
2. Integrate `FilterPanel` for map filters
3. Add heat map overlay toggle
4. Implement cluster marker clicks → `DetailPanel`
5. Add layer controls (clusters, heat map, boundaries)
6. Optimize performance (viewport queries, debounce)

**Files to modify/create:**
- Create: `pages/dashboard/map.tsx`
- Modify: `components/maps/ConflictMap.tsx`
- Create: `components/maps/HeatMapLayer.tsx`
- Create: `components/maps/LayerControls.tsx`

**Agent:** CARTOGRAPHY_AGENT + GEOSPATIAL_AGENT  
**Estimated Time:** 3-4 days

---

### Phase 4: Analytics Pages (Week 3-4) - **DATAVIZ_AGENT**
**Goal:** Build analytics sub-pages per wireframes

**Tasks:**
1. Create `/dashboard/analytics/hotspots` page
2. Create `/dashboard/analytics/trends` page  
3. Create `/dashboard/analytics/correlations` page
4. Create `/dashboard/analytics/archetypes` page
5. Reuse existing chart components
6. Add export functionality (CSV, PDF)

**Files to create:**
- `pages/dashboard/analytics/hotspots.tsx`
- `pages/dashboard/analytics/trends.tsx`
- `pages/dashboard/analytics/correlations.tsx`
- `pages/dashboard/analytics/archetypes.tsx`

**Agent:** DATAVIZ_AGENT + STATISTICIAN_AGENT  
**Estimated Time:** 5-6 days

---

### Phase 5: Forecasting Dashboard (Week 5) - **DATA_SCIENCE_AGENT + DATAVIZ_AGENT**
**Goal:** Complete forecasting UI per wireframes

**Tasks:**
1. Enhance existing `/forecasts` page
2. Add model selector (Ensemble/Prophet/ARIMA)
3. Add location picker (State/LGA)
4. Add forecast horizon slider
5. Build forecast chart with confidence intervals
6. Display model performance metrics
7. Add export functionality

**Files to modify:**
- `pages/forecasts.tsx`
- Create: `components/forecasts/ModelSelector.tsx`
- Create: `components/forecasts/ForecastChart.tsx`
- Create: `components/forecasts/PerformanceMetrics.tsx`

**Agent:** DATA_SCIENCE_AGENT + DATAVIZ_AGENT  
**Estimated Time:** 4-5 days

---

### Phase 6: Incidents & Reports (Week 6) - **API_AGENT**
**Goal:** Build incidents table and reports pages

**Tasks:**
1. Create `/dashboard/incidents` page with table
2. Add advanced filtering, sorting, pagination
3. Build incident detail modal
4. Add export (CSV/Excel)
5. Create `/dashboard/reports` page
6. List pre-generated reports
7. Add PDF download

**Files to create:**
- `pages/dashboard/incidents.tsx`
- `components/incidents/IncidentsTable.tsx`
- `components/incidents/IncidentDetailModal.tsx`
- `pages/dashboard/reports.tsx`

**Agent:** API_AGENT  
**Estimated Time:** 4-5 days

---

### Phase 7: Admin & Monitoring (Week 7) - **INFRA_AGENT + API_AGENT**
**Goal:** Admin-only pages per wireframes

**Tasks:**
1. Create `/dashboard/monitoring` page (Admin only)
2. Display pipeline health, system metrics
3. Add manual trigger controls
4. Create `/dashboard/admin` page (Admin only)
5. User management table
6. Role assignment UI
7. Audit logs display

**Files to create:**
- `pages/dashboard/monitoring.tsx`
- `components/monitoring/PipelineHealth.tsx`
- `components/monitoring/SystemMetrics.tsx`
- `pages/dashboard/admin.tsx`
- `components/admin/UserManagement.tsx`

**Agent:** INFRA_AGENT + API_AGENT  
**Estimated Time:** 4-5 days

---

### Phase 8: Polish & Optimization (Week 8-10) - **QUALITY_ASSURANCE_AGENT**
**Goal:** Accessibility, performance, testing

**Tasks:**
1. Accessibility audit (WCAG 2.1 AA)
2. Add keyboard navigation
3. Screen reader labels
4. Color contrast fixes
5. Performance optimization
   - Code splitting (dynamic imports)
   - Image optimization
   - Bundle size reduction
6. Testing
   - Unit tests (Jest)
   - Integration tests
   - E2E tests (Playwright)
7. Security hardening
   - XSS protection
   - CSRF tokens
   - Content Security Policy

**Agent:** QUALITY_ASSURANCE_AGENT + INFRA_AGENT  
**Estimated Time:** 10-15 days

---

## Agent Assignments Summary

| Phase | Primary Agent | Supporting Agents | Duration |
|-------|--------------|-------------------|----------|
| Phase 1: Layout | DATAVIZ_AGENT | - | 2-3 days |
| Phase 2: Components | DATAVIZ_AGENT | - | 2-3 days |
| Phase 3: Map | CARTOGRAPHY_AGENT | GEOSPATIAL_AGENT | 3-4 days |
| Phase 4: Analytics | DATAVIZ_AGENT | STATISTICIAN_AGENT | 5-6 days |
| Phase 5: Forecasting | DATA_SCIENCE_AGENT | DATAVIZ_AGENT | 4-5 days |
| Phase 6: Incidents | API_AGENT | - | 4-5 days |
| Phase 7: Admin | INFRA_AGENT | API_AGENT | 4-5 days |
| Phase 8: Polish | QUALITY_ASSURANCE_AGENT | INFRA_AGENT | 10-15 days |

**Total:** 8-10 weeks

---

## Quick Wins (Can Start Today)

### 1. Enhance Landing Page (1-2 hours)
- Add recent incidents feed
- Add CTA buttons
- Add feature highlights

### 2. Add Forgot Password Page (2-3 hours)
- Create `/forgot-password` page
- Integrate with password reset API
- Add success/error feedback

### 3. Improve Dashboard Layout (3-4 hours)
- Add user menu dropdown to existing layout
- Add notifications placeholder
- Update navigation styling

### 4. Create FilterPanel Component (4-5 hours)
- Build reusable filter component
- Date range picker
- State/LGA multi-select
- Event type checkboxes

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| **Breaking existing functionality** | Incremental rollout, feature flags, thorough testing |
| **Timeline slippage** | Prioritize high-impact pages, defer nice-to-haves |
| **Performance degradation** | Monitor bundle size, use code splitting, lazy loading |
| **Accessibility gaps** | Automated testing (axe), manual audits, screen reader testing |
| **Mobile responsiveness** | Mobile-first design, test on real devices |

---

## Next Steps (Immediate Actions)

1. **Mark Phase 0 Complete** ✅
2. **Begin Phase 1: Layout Reorganization**
   - Assign to **DATAVIZ_AGENT**
   - Start with Sidebar.tsx component
3. **Create GitHub issues** for each phase
4. **Setup tracking** using bd (beads) for issue management
5. **Daily standup** to monitor progress

---

## Success Metrics

**Functional:**
- ✅ All 15+ pages implemented per wireframes
- ✅ Role-based access enforced
- ✅ Real-time data integration
- ✅ Map functionality preserved and enhanced

**Technical:**
- ✅ TypeScript strict mode
- ✅ Bundle size < 500KB (first load)
- ✅ Lighthouse score > 90
- ✅ Zero critical accessibility violations

**User Experience:**
- ✅ Page load < 2s
- ✅ API response < 500ms
- ✅ Mobile responsive
- ✅ Intuitive navigation

---

## Conclusion

The frontend has **strong bones** - 70% of components exist. The wireframe implementation is primarily about **reorganization and polish** rather than greenfield development. With focused effort across 8 phases and proper agent coordination, we can deliver production-ready UI in 8-10 weeks.

**Recommended Path:** Begin Phase 1 immediately with DATAVIZ_AGENT on sidebar layout.
