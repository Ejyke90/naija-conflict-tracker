# UI/Frontend Wireframe Proposal
**Created:** 2026-01-27  
**Status:** Draft  
**Priority:** High

## Executive Summary

Based on comprehensive backend analysis, this proposal outlines a production-ready UI/UX wireframe for the Nextier Nigeria Conflict Tracker platform. The backend provides robust APIs across 8 core domains with 50+ endpoints. The UI design leverages modern best practices while maintaining accessibility, security, and performance.

---

## Backend Capabilities Analysis

### Core API Domains Discovered

1. **Authentication & Authorization** (`/api/v1/auth`)
   - JWT-based authentication with refresh tokens
   - Role-based access control (Admin, Analyst, Viewer)
   - Session management with Redis
   - Password reset flow
   - Audit logging for security events

2. **Conflict Data Management** (`/api/v1/conflicts`)
   - CRUD operations on conflict events
   - Advanced filtering (state, LGA, date range, event type)
   - Pagination support
   - Summary statistics and aggregations
   - Dashboard-specific queries

3. **Analytics** (`/api/v1/analytics`)
   - Conflict hotspot detection
   - Temporal trends analysis (daily, weekly, monthly)
   - Poverty-conflict correlation
   - Conflict archetype analysis
   - Dashboard summary metrics

4. **Forecasting** (`/api/v1/forecasts`)
   - Prophet model forecasts
   - ARIMA forecasts
   - Ensemble predictions
   - Multi-week forecasting (1-12 weeks ahead)
   - Confidence intervals
   - Model evaluation metrics

5. **Geospatial Analytics** (`/api/v1/spatial`)
   - Proximity-based conflict queries
   - Conflict diffusion index (ACLED-style grid methodology)
   - PostGIS spatial operations
   - Distance calculations

6. **Time-Series Analytics** (`/api/v1/timeseries`)
   - Monthly trend analysis
   - Moving average calculations
   - Anomaly detection
   - Seasonal pattern analysis
   - Simple forecasting
   - Trend comparisons (YoY, MoM)

7. **Location Hierarchy** (`/api/v1/locations`)
   - Nigeria's 36 states
   - 774 LGAs
   - Location hierarchy (state → LGA → community)
   - Geospatial coordinates

8. **System Monitoring** (`/api/v1/monitoring`)
   - Pipeline health status
   - Data quality metrics
   - Scraping status
   - System resource metrics
   - Worker status (Celery)
   - Manual scrape triggers

9. **Public Endpoints** (`/api/v1/public`)
   - Landing page statistics
   - No authentication required
   - Optimized for public consumption

10. **Dashboard APIs** (`/api/dashboard`)
    - UI-optimized data transformations
    - Real-time statistics
    - Recent incidents
    - State-specific data
    - Health checks

---

## User Personas & Use Cases

### 1. **Public Viewer** (No login required)
- Browse conflict data on landing page
- View aggregate statistics
- Access public reports
- See geospatial visualizations

### 2. **Registered Viewer** (Default role after registration)
- All public viewer capabilities
- Access detailed conflict data
- View analytics dashboards
- Download reports
- Create custom filters
- Save preferences

### 3. **Analyst** (Research & policy professionals)
- All viewer capabilities
- Access forecasting models
- Run advanced analytics
- Generate custom reports
- Access correlation analysis
- Export datasets
- View model performance metrics

### 4. **Administrator** (System managers)
- All analyst capabilities
- User management
- System monitoring
- Data quality oversight
- Trigger manual scraping
- Manage permissions
- Access audit logs

---

## Proposed Information Architecture

```
/ (Landing Page - Public)
│
├── /about
├── /methodology
│
├── /login
├── /register
├── /forgot-password
│
└── /dashboard (Protected - Requires Login)
    │
    ├── /overview (Viewer+)
    │   ├── Key metrics cards
    │   ├── Recent incidents
    │   ├── Trend sparklines
    │   └── State-level map
    │
    ├── /map (Viewer+)
    │   ├── Interactive Nigeria map (Mapbox GL JS)
    │   ├── Heat map overlay
    │   ├── Cluster markers
    │   ├── Filters sidebar
    │   │   ├── Date range picker
    │   │   ├── State/LGA selector
    │   │   ├── Event type
    │   │   └── Casualty threshold
    │   └── Details panel (click on marker)
    │
    ├── /analytics (Viewer+)
    │   ├── /hotspots
    │   │   ├── LGA-level heat map
    │   │   ├── Risk level indicators
    │   │   └── Sortable table
    │   │
    │   ├── /trends
    │   │   ├── Time-series charts
    │   │   ├── Period selector (daily/weekly/monthly)
    │   │   ├── State comparison
    │   │   └── Export options
    │   │
    │   ├── /correlations
    │   │   ├── Poverty-conflict scatter plots
    │   │   ├── Statistical significance
    │   │   └── Interactive filters
    │   │
    │   └── /archetypes
    │       ├── Conflict type breakdown
    │       ├── Actor analysis
    │       └── Pattern recognition
    │
    ├── /forecasts (Analyst+)
    │   ├── Model selector (Prophet/ARIMA/Ensemble)
    │   ├── Location picker (state/LGA)
    │   ├── Forecast horizon slider (1-12 weeks)
    │   ├── Confidence interval display
    │   ├── Model performance metrics
    │   ├── Historical vs predicted chart
    │   └── Export forecast data
    │
    ├── /incidents (Viewer+)
    │   ├── Data table with advanced filters
    │   ├── Pagination
    │   ├── Sorting
    │   ├── Detail view modal
    │   ├── Export (CSV/Excel)
    │   └── Create new (Analyst+)
    │
    ├── /reports (Viewer+)
    │   ├── Pre-generated reports
    │   ├── Custom report builder (Analyst+)
    │   ├── PDF download
    │   └── Scheduled reports (Analyst+)
    │
    ├── /monitoring (Admin only)
    │   ├── Pipeline health dashboard
    │   ├── Data quality metrics
    │   ├── System resources
    │   ├── Scraping status
    │   ├── Worker health
    │   └── Manual trigger controls
    │
    ├── /admin (Admin only)
    │   ├── User management
    │   ├── Role assignments
    │   ├── Audit logs
    │   └── System settings
    │
    └── /profile (All authenticated users)
        ├── Personal information
        ├── Change password
        ├── Session management
        └── API token generation
```

---

## Page-by-Page Wireframes

### 1. Landing Page (Public)

**Purpose:** Engage visitors, showcase platform value, drive registrations

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  [LOGO]  Nextier Conflict Tracker    [Login] [Register] │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │        HERO SECTION                             │   │
│  │  Track, Analyze, Predict Violence in Nigeria   │   │
│  │                                                   │   │
│  │  [Get Started Free →]  [View Demo]              │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────┐   │
│  │ 1,234    │  │  892     │  │  18      │  │ 15   │   │
│  │ Incidents│  │Fatalities│  │Hotspots  │  │States│   │
│  │ (30 days)│  │ (30 days)│  │          │  │      │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────┘   │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │                                                   │   │
│  │       INTERACTIVE MAP OF NIGERIA                 │   │
│  │       (Heat map showing conflict density)        │   │
│  │                                                   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  ┌──────────────────────────────────────┐              │
│  │  RECENT INCIDENTS (Public Preview)   │              │
│  │                                        │              │
│  │  📍 Kaduna State - Armed Conflict     │              │
│  │     Jan 25, 2026 | 12 casualties     │              │
│  │                                        │              │
│  │  📍 Borno State - Terrorist Attack    │              │
│  │     Jan 24, 2026 | 8 casualties      │              │
│  │                                        │              │
│  │  [View All Incidents →]               │              │
│  └──────────────────────────────────────┘              │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  FEATURE HIGHLIGHTS                             │   │
│  │                                                   │   │
│  │  [🗺️ Geospatial]  [📊 Analytics]  [🔮 Forecast]│   │
│  │   Visualization     Real-time       ML-powered  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  FOOTER: About | Methodology | API Docs | Contact      │
└─────────────────────────────────────────────────────────┘
```

**Components:**
- Hero section with value proposition
- Live statistics cards (via `/api/v1/public/landing-stats`)
- Interactive map preview (Mapbox GL JS)
- Recent incidents feed (limited to 5)
- Feature highlights
- Call-to-action buttons

**Data Sources:**
- `GET /api/v1/public/landing-stats` - Hero metrics
- `GET /api/v1/conflicts?limit=5` - Recent incidents (public subset)

---

### 2. Authentication Pages

#### Login Page
```
┌─────────────────────────────────────────┐
│  [← Back to Home]                       │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   [LOGO]                        │   │
│  │                                 │   │
│  │   Login to Your Account        │   │
│  │                                 │   │
│  │   Email                         │   │
│  │   [_________________]           │   │
│  │                                 │   │
│  │   Password                      │   │
│  │   [_________________] [👁️]      │   │
│  │                                 │   │
│  │   [ ] Remember me               │   │
│  │                                 │   │
│  │   [Login →]                     │   │
│  │                                 │   │
│  │   Forgot password?              │   │
│  │                                 │   │
│  │   Don't have account? Register  │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**API:** `POST /api/v1/auth/login`

**Features:**
- Email validation
- Password visibility toggle
- Remember me checkbox
- Error handling (invalid credentials, rate limiting)
- Redirect to dashboard on success
- Session persistence

#### Register Page
```
┌─────────────────────────────────────────┐
│  [← Back to Home]                       │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   [LOGO]                        │   │
│  │                                 │   │
│  │   Create Your Account          │   │
│  │                                 │   │
│  │   Full Name                     │   │
│  │   [_________________]           │   │
│  │                                 │   │
│  │   Email                         │   │
│  │   [_________________]           │   │
│  │                                 │   │
│  │   Password                      │   │
│  │   [_________________]           │   │
│  │   ● Strong  ✓ 8+ chars ✓ Number│   │
│  │                                 │   │
│  │   Confirm Password              │   │
│  │   [_________________]           │   │
│  │                                 │   │
│  │   [ ] I agree to Terms         │   │
│  │                                 │   │
│  │   [Create Account →]            │   │
│  │                                 │   │
│  │   Already registered? Login     │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**API:** `POST /api/v1/auth/register`

**Features:**
- Real-time password strength indicator
- Email uniqueness validation
- Password confirmation matching
- Terms acceptance
- Auto-assign "viewer" role
- Success → redirect to dashboard

---

### 3. Dashboard Overview (Protected - Viewer+)

```
┌─────────────────────────────────────────────────────────────────┐
│ [☰] Nigeria Conflict Tracker    [🔔] [👤 User ▾]               │
├──────┬──────────────────────────────────────────────────────────┤
│      │                                                           │
│ 📊   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│ Over │  │ 1,234    │  │  892     │  │  18      │  │  6       ││
│ view │  │Incidents │  │Fatalities│  │Hotspots  │  │ States   ││
│      │  │ ↑12%     │  │ ↓8%      │  │ ↑2       │  │ →0%      ││
│ 🗺️    │  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
│ Map  │                                                           │
│      │  ┌─────────────────────────────┐  ┌──────────────────┐ │
│ 📈   │  │ TREND CHART                 │  │ TOP HOTSPOTS     │ │
│ Analy│  │                             │  │                  │ │
│ tics │  │ Incidents over time         │  │ 1. Zamfara       │ │
│      │  │      ╱╲   ╱╲               │  │ 2. Kaduna        │ │
│ 🔮   │  │    ╱    ╲╱  ╲              │  │ 3. Borno         │ │
│ Fore │  │  ╱             ╲            │  │ 4. Plateau       │ │
│ cast │  │╱                 ╲          │  │ 5. Taraba        │ │
│      │  │                             │  │                  │ │
│ 📋   │  └─────────────────────────────┘  └──────────────────┘ │
│ Inci │                                                           │
│ dents│  ┌──────────────────────────────────────────────────┐  │
│      │  │ RECENT INCIDENTS                                 │  │
│ 📊   │  │                                                   │  │
│ Repo │  │ 📍 Kaduna | Armed Conflict | 12 casualties       │  │
│ rts  │  │    Jan 25, 2026 | Verified  [View Details →]    │  │
│      │  │                                                   │  │
│ 🔧   │  │ 📍 Borno | Terrorist Attack | 8 casualties       │  │
│ Moni │  │    Jan 24, 2026 | Verified  [View Details →]    │  │
│ tor* │  │                                                   │  │
│      │  │ [View All →]                                     │  │
│ 👥   │  └──────────────────────────────────────────────────┘  │
│ Admin│                                                           │
│  *   │                                                           │
│      │                                                           │
│ 👤   │                                                           │
│ Profi│                                                           │
│ le   │                                                           │
└──────┴──────────────────────────────────────────────────────────┘

* Admin only
```

**Navigation Sidebar:**
- Collapsible/expandable
- Icons + labels
- Role-based menu items
- Active state highlighting
- Responsive (mobile drawer)

**Top Bar:**
- Platform branding
- Notifications bell (system alerts)
- User menu dropdown:
  - Profile
  - Settings
  - Logout

**Overview Content:**
- KPI cards with trend indicators
- Time-series chart (last 6 months)
- Top hotspots list
- Recent incidents feed
- Quick action buttons

**Data Sources:**
- `GET /api/v1/analytics/dashboard-summary` - KPIs
- `GET /api/v1/analytics/trends?period=monthly&months=6` - Chart data
- `GET /api/v1/analytics/hotspots?limit=5` - Hotspots
- `GET /api/v1/conflicts?limit=10` - Recent incidents

---

### 4. Interactive Map Page (Viewer+)

```
┌─────────────────────────────────────────────────────────────────┐
│ [☰] Map View                            [🔔] [👤 User ▾]        │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│ ┌──────────┐                                                     │
│ │ FILTERS  │                                                     │
│ ├──────────┤                                                     │
│ │ Date Range                                                     │
│ │ [Last 30 days ▾]                                              │
│ │                                                                 │
│ │ States                                                         │
│ │ [All States ▾]                                                │
│ │                                                                 │
│ │ Event Type                                                     │
│ │ [ ] Armed Conflict                                            │
│ │ [ ] Terrorist Attack                                          │
│ │ [ ] Communal Clash                                            │
│ │ [ ] Kidnapping                                                │
│ │                                                                 │
│ │ Casualties                                                     │
│ │ Min: [0] Max: [100+]                                          │
│ │                                                                 │
│ │ [Reset] [Apply Filters]                                       │
│ └──────────┘                                                     │
│                                                                   │
│              ┌─────────────────────────────────────────┐        │
│              │                                         │        │
│              │  🗺️  INTERACTIVE NIGERIA MAP           │        │
│              │                                         │        │
│              │  [Cluster markers]                     │        │
│              │  [Heat map overlay]                    │        │
│              │  [State boundaries]                    │        │
│              │                                         │        │
│              │  Click markers for details →           │        │
│              │                                         │        │
│              │  [+] [-] [📍] [🔍] [🌐]                │        │
│              │                                         │        │
│              └─────────────────────────────────────────┘        │
│                                                                   │
│              ┌─────────────────────────┐                        │
│              │ SELECTED INCIDENT       │ (Appears on click)    │
│              ├─────────────────────────┤                        │
│              │ Kaduna State            │                        │
│              │ Armed Conflict          │                        │
│              │ Jan 25, 2026           │                        │
│              │                         │                        │
│              │ Fatalities: 12          │                        │
│              │ Injuries: 8             │                        │
│              │ Location: Zaria LGA     │                        │
│              │                         │                        │
│              │ Actors:                 │                        │
│              │ - Armed group           │                        │
│              │ - Civilian population   │                        │
│              │                         │                        │
│              │ Source: Premium Times   │                        │
│              │ Verified: ✓ Yes         │                        │
│              │                         │                        │
│              │ [View Full Report →]    │                        │
│              └─────────────────────────┘                        │
└──────────────────────────────────────────────────────────────────┘
```

**Map Features:**
- Mapbox GL JS integration
- Cluster markers (aggregate nearby incidents)
- Heat map overlay (density visualization)
- State/LGA boundary overlays
- Zoom controls
- Geolocation button
- Search/geocoding
- Layer toggles (clusters, heat map, boundaries)

**Filter Panel:**
- Sticky position
- Collapsible on mobile
- Multi-select dropdowns
- Date range picker (preset + custom)
- Real-time filter application
- Filter count badges
- Reset functionality

**Detail Panel:**
- Slides in from right on marker click
- Incident metadata
- Actor information
- Verification status
- Source attribution
- Link to full incident detail

**Data Sources:**
- `GET /api/v1/conflicts?state={state}&start_date={date}&end_date={date}` - Filtered incidents
- `GET /api/v1/spatial/proximity/{lat}/{lng}?radius_km=50` - Proximity search
- `GET /api/v1/locations/hierarchy` - State/LGA boundaries

**Performance Optimizations:**
- Marker clustering for large datasets
- Lazy loading of incident details
- Debounced filter updates
- Map viewport-based queries

---

### 5. Analytics - Hotspots Page (Viewer+)

```
┌─────────────────────────────────────────────────────────────────┐
│ [☰] Analytics → Hotspots                [🔔] [👤 User ▾]        │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  CONFLICT HOTSPOTS ANALYSIS                                      │
│  Identify areas with highest concentration of violence           │
│                                                                   │
│  ┌─────────────────────────────────────────┐                    │
│  │ Timeframe: [Last 6 months ▾]            │                    │
│  │ Min Incidents: [5 ▾]                    │                    │
│  │ Radius: [50 km ▾]                       │                    │
│  │ [Update Analysis]                       │                    │
│  └─────────────────────────────────────────┘                    │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                                                           │   │
│  │  🗺️  HEAT MAP VISUALIZATION                             │   │
│  │                                                           │   │
│  │  [Red zones indicate high-conflict areas]                │   │
│  │  [State boundaries overlaid]                             │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ HOTSPOT RANKINGS                                         │   │
│  ├──────┬─────────────┬──────────┬────────────┬────────────┤   │
│  │ Rank │ Location    │Incidents │ Fatalities │ Risk Level │   │
│  ├──────┼─────────────┼──────────┼────────────┼────────────┤   │
│  │  1   │ Zamfara     │   156    │    432     │ 🔴 Critical│   │
│  │  2   │ Kaduna      │   142    │    389     │ 🔴 Critical│   │
│  │  3   │ Borno       │   128    │    356     │ 🔴 Critical│   │
│  │  4   │ Plateau     │    98    │    234     │ 🟠 High    │   │
│  │  5   │ Taraba      │    87    │    198     │ 🟠 High    │   │
│  │  6   │ Niger       │    76    │    167     │ 🟠 High    │   │
│  │  7   │ Adamawa     │    65    │    145     │ 🟡 Moderate│   │
│  │  8   │ Benue       │    54    │    123     │ 🟡 Moderate│   │
│  │  ... │             │          │            │            │   │
│  └──────┴─────────────┴──────────┴────────────┴────────────┘   │
│  [Export CSV] [Export PDF]                                      │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ LGA-LEVEL BREAKDOWN (Click state to expand)              │   │
│  │                                                           │   │
│  │ ▾ Zamfara State (156 incidents)                          │   │
│  │   1. Anka LGA - 45 incidents                             │   │
│  │   2. Gusau LGA - 38 incidents                            │   │
│  │   3. Maru LGA - 32 incidents                             │   │
│  │   ...                                                     │   │
│  │                                                           │   │
│  │ ▸ Kaduna State (142 incidents)                           │   │
│  │                                                           │   │
│  │ ▸ Borno State (128 incidents)                            │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

**Components:**
- Control panel (timeframe, parameters)
- Heat map visualization
- Sortable data table
- Risk level color coding
- Drill-down capability (state → LGA)
- Export functionality

**Data Sources:**
- `GET /api/v1/analytics/hotspots?radius_km=50&min_incidents=5` - Hotspot data
- `GET /api/v1/conflicts?state={state}&start_date={date}` - LGA breakdown

**UX Considerations:**
- Color-blind friendly palette
- Sortable columns
- Pagination for large datasets
- Tooltip explanations for risk levels

---

### 6. Forecasting Dashboard (Analyst+)

```
┌─────────────────────────────────────────────────────────────────┐
│ [☰] Forecasts                           [🔔] [👤 User ▾]        │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  CONFLICT FORECASTING - ML-Powered Predictions                   │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ CONFIGURATION                                          │     │
│  ├────────────────────────────────────────────────────────┤     │
│  │ Location Type: (•) State  ( ) LGA                      │     │
│  │                                                         │     │
│  │ Select Location: [Kaduna State ▾]                      │     │
│  │                                                         │     │
│  │ Model:                                                  │     │
│  │ (•) Ensemble (Recommended)                             │     │
│  │ ( ) Prophet (Best for long-term trends)                │     │
│  │ ( ) ARIMA (Best for short-term volatility)             │     │
│  │                                                         │     │
│  │ Forecast Horizon: [4] weeks ahead                      │     │
│  │ ├──────────●────────────────────┤ (1-12 weeks)         │     │
│  │                                                         │     │
│  │ [Generate Forecast]                                    │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ FORECAST VISUALIZATION                                 │     │
│  │                                                         │     │
│  │     Predicted Incidents (with 95% confidence interval) │     │
│  │                                                         │     │
│  │ 40│                              ┌───┐                 │     │
│  │   │                         ┌───┐│   │┌───┐           │     │
│  │ 30│                    ┌───┐│   ││   ││   │           │     │
│  │   │               ┌───┐│   ││   ││   ││   │           │     │
│  │ 20│          ┌───┐│   ││   ││   ││   ││   │           │     │
│  │   │     ┌───┐│   ││   ││   ││   ││   ││   │           │     │
│  │ 10│┌───┐│   ││   ││   ││   ││   ││   ││   │           │     │
│  │   ├────┴────┴────┴────┴────┴────┴────┴────┴──────────▶│     │
│  │    Week Week Week Week Week Week Week Week             │     │
│  │     -4   -3   -2   -1   +1   +2   +3   +4             │     │
│  │                                                         │     │
│  │    ━━━ Actual  ━━━ Forecast  ▒▒▒ 95% CI               │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ NEXT WEEK    │  │ 2 WEEKS      │  │ 4 WEEKS      │          │
│  │              │  │              │  │              │          │
│  │   28         │  │   32         │  │   38         │          │
│  │ Predicted    │  │ Predicted    │  │ Predicted    │          │
│  │ Incidents    │  │ Incidents    │  │ Incidents    │          │
│  │              │  │              │  │              │          │
│  │ ±4 (95% CI)  │  │ ±6 (95% CI)  │  │ ±9 (95% CI)  │          │
│  │ 🟠 Moderate  │  │ 🟠 Moderate  │  │ 🔴 High      │          │
│  │ Risk         │  │ Risk         │  │ Risk         │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ MODEL PERFORMANCE                                      │     │
│  ├────────────────────────────────────────────────────────┤     │
│  │ Model: Ensemble (Prophet + ARIMA)                     │     │
│  │ Training Data: 24 months (Jan 2024 - Dec 2025)        │     │
│  │ Last Updated: Jan 27, 2026 09:30 AM                   │     │
│  │                                                         │     │
│  │ Accuracy Metrics:                                      │     │
│  │ • MAE (Mean Absolute Error): 2.8 incidents/week        │     │
│  │ • RMSE (Root Mean Squared Error): 4.1                 │     │
│  │ • MAPE (Mean Absolute % Error): 12.3%                 │     │
│  │ • R² Score: 0.76 (Good fit)                            │     │
│  │                                                         │     │
│  │ [View Model Details] [Download Forecast Data]         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ INDIVIDUAL MODEL COMPARISON (Ensemble only)            │     │
│  ├──────────┬──────────┬──────────┬──────────┬──────────┤     │
│  │ Week     │ Prophet  │ ARIMA    │ Ensemble │ Actual   │     │
│  ├──────────┼──────────┼──────────┼──────────┼──────────┤     │
│  │ Week +1  │   26     │   30     │   28     │   -      │     │
│  │ Week +2  │   29     │   35     │   32     │   -      │     │
│  │ Week +3  │   31     │   39     │   35     │   -      │     │
│  │ Week +4  │   34     │   42     │   38     │   -      │     │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘     │
└──────────────────────────────────────────────────────────────────┘
```

**Features:**
- Model selection with descriptions
- Location picker
- Adjustable forecast horizon
- Confidence interval visualization
- Key predictions cards
- Model performance metrics
- Individual model comparison (ensemble)
- Export forecast data

**Data Sources:**
- `GET /api/v1/forecasts/advanced/{location_name}?model=ensemble&weeks_ahead=4` - Generate forecast
- Model metadata included in response

**UX Best Practices:**
- Clear model explanations
- Uncertainty communication (confidence intervals)
- Performance transparency
- Interactive chart with hover tooltips
- Downloadable data for further analysis

---

### 7. Incidents Data Table (Viewer+)

```
┌─────────────────────────────────────────────────────────────────┐
│ [☰] Incidents                           [🔔] [👤 User ▾]        │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  CONFLICT INCIDENTS DATABASE                                     │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ [🔍 Search...]  [Date ▾] [State ▾] [Type ▾] [+ New]*    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  1,234 incidents found    [Export CSV] [Export Excel]            │
│                                                                   │
│  ┌─────┬──────────┬───────────┬──────────┬──────────┬─────────┐│
│  │     │ Date ▼   │ Location  │ Type     │Casualties│ Status  ││
│  ├─────┼──────────┼───────────┼──────────┼──────────┼─────────┤│
│  │ [👁️]│ Jan 25   │ Kaduna    │ Armed    │    20    │ ✓ Verif ││
│  │     │ 2026     │ State     │ Conflict │ (12+8)   │ ied     ││
│  ├─────┼──────────┼───────────┼──────────┼──────────┼─────────┤│
│  │ [👁️]│ Jan 24   │ Borno     │ Terror   │     8    │ ✓ Verif ││
│  │     │ 2026     │ State     │ Attack   │ (8+0)    │ ied     ││
│  ├─────┼──────────┼───────────┼──────────┼──────────┼─────────┤│
│  │ [👁️]│ Jan 23   │ Zamfara   │ Communal │    15    │ ⏳ Pend ││
│  │     │ 2026     │ State     │ Clash    │ (6+9)    │ ing     ││
│  ├─────┼──────────┼───────────┼──────────┼──────────┼─────────┤│
│  │ ... │          │           │          │          │         ││
│  └─────┴──────────┴───────────┴──────────┴──────────┴─────────┘│
│                                                                   │
│  [◀ Previous]  Page 1 of 124  [Next ▶]                          │
│                                                                   │
│  * Analyst+ only                                                 │
└──────────────────────────────────────────────────────────────────┘
```

**Detail Modal (Click 👁️):**
```
┌─────────────────────────────────────┐
│ INCIDENT DETAILS             [✕]    │
├─────────────────────────────────────┤
│                                     │
│ ID: 12abc-345-def-678              │
│ Date: January 25, 2026             │
│                                     │
│ Location:                           │
│ • State: Kaduna                     │
│ • LGA: Zaria                        │
│ • Coordinates: 11.11°N, 7.71°E     │
│                                     │
│ Event Type: Armed Conflict          │
│ Category: Violence Against Civilians│
│ Archetype: Banditry                 │
│                                     │
│ Actors:                             │
│ • Primary: Armed bandit group       │
│ • Secondary: Civilian population    │
│                                     │
│ Casualties:                         │
│ • Fatalities: 12                    │
│ • Injuries: 8                       │
│ • Displaced: 150                    │
│                                     │
│ Source: Premium Times               │
│ Verified: ✓ Yes                     │
│ Confidence: High                    │
│                                     │
│ Notes:                              │
│ Attack occurred on market day...    │
│                                     │
│ [Edit]* [Delete]** [Close]          │
│                                     │
│ * Analyst+  ** Admin only           │
└─────────────────────────────────────┘
```

**Features:**
- Advanced search
- Multi-column sorting
- Filter dropdowns
- Pagination (100 items/page)
- Bulk export
- Detail modal
- Role-based actions (Create/Edit/Delete)

**Data Sources:**
- `GET /api/v1/conflicts?skip=0&limit=100&state={state}&event_type={type}` - List incidents
- `GET /api/v1/conflicts/{conflict_id}` - Incident details
- `POST /api/v1/conflicts` - Create new (Analyst+)
- `PUT /api/v1/conflicts/{conflict_id}` - Update (Analyst+)
- `DELETE /api/v1/conflicts/{conflict_id}` - Delete (Admin only)

**Performance:**
- Virtual scrolling for large datasets
- Debounced search
- Cached filter options
- Lazy loading of details

---

### 8. System Monitoring Dashboard (Admin Only)

```
┌─────────────────────────────────────────────────────────────────┐
│ [☰] Monitoring                          [🔔] [👤 Admin ▾]       │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  SYSTEM HEALTH & MONITORING                                      │
│                                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ API      │  │ DATABASE │  │ REDIS    │  │ WORKERS  │        │
│  │ ✅ Healthy│  │ ✅ Online │  │ ✅ Online │  │ ✅ 3/3   │        │
│  │ 99.9%    │  │ 23ms RTT │  │ 12ms RTT │  │ Active   │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ PIPELINE STATUS                                        │     │
│  ├────────────────────────────────────────────────────────┤     │
│  │ Overall: ✅ Healthy                                     │     │
│  │ Last Run: 2 minutes ago                                │     │
│  │ Next Scheduled: 58 minutes                             │     │
│  │                                                         │     │
│  │ Scraping Health:                                       │     │
│  │ ✅ Premium Times - Success (32 articles)               │     │
│  │ ✅ Vanguard - Success (28 articles)                    │     │
│  │ ⚠️  Daily Trust - Partial (18/25 articles)            │     │
│  │ ❌ Punch - Failed (Rate limit)                         │     │
│  │                                                         │     │
│  │ [Trigger Manual Scrape] [View Logs]                   │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ DATA QUALITY METRICS                                   │     │
│  ├────────────────────────────────────────────────────────┤     │
│  │ Total Events: 12,456                                   │     │
│  │ Verified: 11,234 (90.2%)                               │     │
│  │ Pending Review: 1,222 (9.8%)                           │     │
│  │                                                         │     │
│  │ Geocoding Coverage: 87.3%                              │     │
│  │ Duplicate Rate: 2.1% (within threshold)                │     │
│  │                                                         │     │
│  │ ⚠️  ALERTS:                                             │     │
│  │ • 15 events missing coordinates                        │     │
│  │ • Unusual spike detected in Zamfara (+45% vs avg)      │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ SYSTEM RESOURCES                                       │     │
│  ├────────────────────────────────────────────────────────┤     │
│  │ CPU Usage:    [████████░░] 82%                         │     │
│  │ Memory:       [██████░░░░] 68% (4.2 GB / 6 GB)         │     │
│  │ Disk:         [███░░░░░░░] 34% (68 GB / 200 GB)        │     │
│  │                                                         │     │
│  │ Database Connections:                                  │     │
│  │ Pool Size: 20 | Active: 8 | Idle: 12                  │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ WORKER STATUS                                          │     │
│  ├────────────────────────────────────────────────────────┤     │
│  │ Worker 1: ✅ Active | Processing: scraping_task        │     │
│  │ Worker 2: ✅ Active | Processing: geocoding_batch      │     │
│  │ Worker 3: ✅ Idle   | Last task: 3 minutes ago         │     │
│  └────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────┘
```

**Data Sources:**
- `GET /api/v1/monitoring/pipeline-status` - Pipeline health
- `GET /api/v1/monitoring/system-metrics` - System resources
- `GET /api/v1/monitoring/worker-status` - Celery workers
- `GET /api/v1/monitoring/data-quality` - Quality metrics
- `POST /api/v1/monitoring/trigger-manual` - Manual scrape

**Features:**
- Real-time health indicators
- Scraping source status
- Data quality dashboards
- System resource monitoring
- Worker management
- Alert notifications
- Manual trigger controls

---

## Design System & Component Library

### Color Palette

**Brand Colors:**
- Primary: `#1E40AF` (Deep Blue) - Trust, stability
- Secondary: `#059669` (Emerald Green) - Growth, Nigeria flag
- Accent: `#DC2626` (Red) - Urgency, alerts

**Severity Colors:**
- Critical: `#DC2626` (Red) - High risk
- High: `#F59E0B` (Amber) - Elevated risk
- Moderate: `#FBBF24` (Yellow) - Moderate risk
- Low: `#10B981` (Green) - Low risk
- Info: `#3B82F6` (Blue) - Information

**Neutral Colors:**
- Background: `#F9FAFB` (Light gray)
- Surface: `#FFFFFF` (White)
- Border: `#E5E7EB` (Gray 200)
- Text Primary: `#111827` (Gray 900)
- Text Secondary: `#6B7280` (Gray 500)

**Status Colors:**
- Success: `#10B981` (Green)
- Warning: `#F59E0B` (Amber)
- Error: `#EF4444` (Red)
- Verified: `#059669` (Emerald)

### Typography

**Font Family:**
- Primary: Inter (sans-serif) - Modern, readable
- Monospace: JetBrains Mono - Code, IDs

**Type Scale:**
- H1: 36px / 2.25rem (Page titles)
- H2: 30px / 1.875rem (Section headers)
- H3: 24px / 1.5rem (Subsections)
- H4: 20px / 1.25rem (Card headers)
- Body: 16px / 1rem (Main text)
- Small: 14px / 0.875rem (Labels, captions)
- Tiny: 12px / 0.75rem (Metadata)

### Spacing System

- xs: 4px / 0.25rem
- sm: 8px / 0.5rem
- md: 16px / 1rem
- lg: 24px / 1.5rem
- xl: 32px / 2rem
- 2xl: 48px / 3rem

### Components

**Buttons:**
- Primary: Filled, high contrast
- Secondary: Outlined, lower emphasis
- Tertiary: Text only, minimal
- States: Default, Hover, Active, Disabled

**Cards:**
- White background
- Subtle shadow
- Rounded corners (8px)
- Padding: 16-24px

**Forms:**
- Clear labels
- Inline validation
- Error states
- Helper text
- Required field indicators

**Data Tables:**
- Zebra striping (optional)
- Sortable headers
- Row hover states
- Fixed header on scroll
- Pagination controls

**Charts:**
- Recharts library (React)
- Consistent color scheme
- Tooltips on hover
- Legends
- Responsive sizing
- Export SVG/PNG

**Maps:**
- Mapbox GL JS
- Custom markers
- Cluster thresholds
- Heat map gradients
- Layer controls

### Accessibility (WCAG 2.1 AA)

**Color Contrast:**
- Text on backgrounds: Minimum 4.5:1 ratio
- Large text (18pt+): Minimum 3:1 ratio
- Icons and controls: Minimum 3:1 ratio

**Keyboard Navigation:**
- Tab order matches visual order
- Focus indicators on all interactive elements
- Skip navigation links
- Escape key closes modals

**Screen Readers:**
- Semantic HTML (header, nav, main, footer)
- ARIA labels on complex components
- Alt text for images
- Form labels properly associated

**Motion:**
- Respect `prefers-reduced-motion`
- Optional animations
- No auto-playing videos

---

## State Management & Data Flow

### Frontend State Architecture

**Technology:** React Context API + SWR (or React Query)

**State Layers:**

1. **Authentication State** (Global)
   - User object
   - Access token
   - Refresh token
   - Session expiry
   - Role permissions

2. **UI State** (Page-level)
   - Filter selections
   - Pagination state
   - Sort preferences
   - Modal visibility
   - Sidebar collapsed state

3. **Server State** (SWR/React Query)
   - Cached API responses
   - Loading states
   - Error states
   - Automatic revalidation
   - Optimistic updates

**Data Flow:**
```
User Action → API Request → Backend → Response
    ↓                                      ↓
UI Update ← Cache Update ← Parse JSON ←---┘
```

**Caching Strategy:**
- Short TTL (30s): Dashboard stats, recent incidents
- Medium TTL (5min): Conflict data, analytics
- Long TTL (1hr): Forecasts, static data (states, LGAs)
- Invalidation: On mutations (create/update/delete)

---

## Performance Optimization

### Frontend Optimizations

1. **Code Splitting:**
   - Route-based splitting
   - Dynamic imports for large components
   - Lazy load modals and charts

2. **Image Optimization:**
   - Next.js Image component
   - WebP format
   - Responsive images
   - Lazy loading

3. **Bundle Size:**
   - Tree shaking
   - Remove unused dependencies
   - Analyze bundle composition
   - Target: <200KB initial JS

4. **Rendering:**
   - React.memo for expensive components
   - Virtual scrolling for large lists
   - Debounced inputs
   - Throttled scroll handlers

5. **API Calls:**
   - Request deduplication
   - Parallel requests where possible
   - Pagination for large datasets
   - Compression (gzip/brotli)

### Backend Optimizations (Already Implemented)

- Redis caching (1hr TTL for forecasts)
- Database connection pooling
- Query optimization
- Indexed columns (state, date, event_type)
- Async operations
- Background tasks (Celery)

### Performance Targets

- **Time to Interactive:** <3 seconds
- **Largest Contentful Paint:** <2.5 seconds
- **Cumulative Layout Shift:** <0.1
- **First Input Delay:** <100ms
- **Lighthouse Score:** >90

---

## Security Considerations

### Frontend Security

1. **Authentication:**
   - Secure token storage (httpOnly cookies preferred, or localStorage with XSS protections)
   - Automatic token refresh
   - Session timeout handling
   - Logout on token expiry

2. **Authorization:**
   - Client-side route guards
   - Component-level permissions
   - Disabled UI for unauthorized actions
   - Backend validation (never trust frontend)

3. **XSS Prevention:**
   - React's built-in escaping
   - Sanitize HTML if rendering user content
   - CSP headers

4. **CSRF Protection:**
   - SameSite cookies
   - CSRF tokens for mutations
   - Verify origin headers

5. **Data Validation:**
   - Input validation
   - Type checking (TypeScript)
   - Sanitize before API calls

### HTTPS & Transport

- All communications over HTTPS
- Secure WebSocket connections (WSS) if real-time features added
- HSTS headers
- Certificate pinning (mobile apps)

### Sensitive Data Handling

- No plaintext passwords
- No API keys in frontend code
- Environment variables for configs
- Redact sensitive data in logs

---

## Mobile Responsiveness

### Breakpoints

- **Mobile:** 320px - 640px
- **Tablet:** 641px - 1024px
- **Desktop:** 1025px+
- **Large Desktop:** 1440px+

### Mobile-Specific Adaptations

**Navigation:**
- Hamburger menu (collapsed sidebar)
- Bottom tab bar (optional)
- Swipe gestures

**Map:**
- Touch gestures (pinch, zoom, pan)
- Larger tap targets
- Simplified controls

**Tables:**
- Horizontal scroll
- Stacked card view (mobile)
- Expandable rows

**Charts:**
- Touch-friendly tooltips
- Simplified legends
- Responsive sizing

**Forms:**
- Full-width inputs
- Native input types (date, email)
- Auto-capitalize, autocomplete
- Visible focus states

### Progressive Web App (PWA)

**Future Enhancement:**
- Offline support
- Add to home screen
- Push notifications
- Background sync

---

## Internationalization (Future)

**Languages:**
- English (primary)
- Hausa
- Yoruba
- Igbo

**Implementation:**
- i18next library
- JSON translation files
- Language switcher in header
- RTL support (if needed)

---

## Analytics & Monitoring

### User Analytics (Privacy-Respectful)

**Track:**
- Page views
- Feature usage
- Click events
- Search queries
- Error rates
- Session duration

**Tools:**
- Plausible Analytics (privacy-focused)
- Or Google Analytics with anonymization

### Error Tracking

**Frontend:**
- Sentry for error monitoring
- Source maps for debugging
- User context (role, page)
- Breadcrumbs

**Backend:**
- Already has logging
- Integrate with Sentry
- Alert on critical errors

### Performance Monitoring

- Real User Monitoring (RUM)
- API response times
- Render performance
- Bundle size tracking

---

## Testing Strategy

### Frontend Tests

1. **Unit Tests:**
   - Component logic
   - Utility functions
   - State management
   - Tool: Jest + React Testing Library

2. **Integration Tests:**
   - API integration
   - Multi-component flows
   - Form submissions
   - Tool: Jest + MSW (Mock Service Worker)

3. **E2E Tests:**
   - Critical user flows
   - Login → Dashboard → Map
   - Analyst forecasting workflow
   - Tool: Playwright or Cypress

4. **Visual Regression:**
   - Component snapshots
   - Tool: Percy or Chromatic

### Accessibility Tests

- axe-core automated testing
- Manual screen reader testing
- Keyboard navigation testing

### Performance Tests

- Lighthouse CI
- Bundle size limits
- Load testing (k6)

---

## Deployment & CI/CD

### Frontend Deployment

**Platform:** Vercel (already configured)

**Build Process:**
1. Install dependencies (`npm install`)
2. Run linting (`npm run lint`)
3. Run tests (`npm test`)
4. Build production (`npm run build`)
5. Deploy to Vercel

**Environment Variables:**
- `NEXT_PUBLIC_API_URL` - Backend API URL
- `NEXT_PUBLIC_MAPBOX_TOKEN` - Mapbox access token
- `NEXT_PUBLIC_ENV` - Environment name

**Environments:**
- Development (local)
- Staging (Vercel preview)
- Production (Vercel main branch)

### Backend Deployment

**Platform:** Railway (already configured)

### CI/CD Pipeline

**GitHub Actions:**
```yaml
# .github/workflows/frontend.yml
name: Frontend CI/CD
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    - Install dependencies
    - Run linters
    - Run unit tests
    - Run E2E tests (on PRs)
  
  build:
    - Build Next.js app
    - Check bundle size
    - Upload build artifacts
  
  deploy:
    - Deploy to Vercel (auto on main)
```

---

## Implementation Roadmap

### Phase 1: Core UI Foundation (Weeks 1-2)

**Sprint 1.1 - Authentication & Layout**
- [ ] Design system setup (colors, typography, components)
- [ ] Login/Register pages
- [ ] Dashboard layout shell
- [ ] Navigation sidebar
- [ ] Top bar with user menu
- [ ] Role-based routing

**Sprint 1.2 - Landing Page**
- [ ] Hero section
- [ ] Statistics cards (API integration)
- [ ] Map preview
- [ ] Recent incidents feed
- [ ] Footer

**Deliverable:** Functional authentication + landing page

---

### Phase 2: Data Visualization (Weeks 3-4)

**Sprint 2.1 - Dashboard Overview**
- [ ] KPI cards with trends
- [ ] Time-series chart component
- [ ] Top hotspots list
- [ ] Recent incidents table
- [ ] API integration

**Sprint 2.2 - Interactive Map**
- [ ] Mapbox GL JS integration
- [ ] Marker clustering
- [ ] Heat map overlay
- [ ] Filter panel
- [ ] Detail panel
- [ ] Location search

**Deliverable:** Core data visualization features

---

### Phase 3: Analytics & Insights (Weeks 5-6)

**Sprint 3.1 - Analytics Pages**
- [ ] Hotspots page (heat map + table)
- [ ] Trends page (time-series charts)
- [ ] Correlation analysis page
- [ ] Archetype breakdown

**Sprint 3.2 - Forecasting Dashboard**
- [ ] Model configuration panel
- [ ] Forecast visualization
- [ ] Confidence intervals
- [ ] Model performance metrics
- [ ] Export functionality

**Deliverable:** Full analytics suite

---

### Phase 4: Data Management (Weeks 7-8)

**Sprint 4.1 - Incidents Table**
- [ ] Data table component
- [ ] Advanced filters
- [ ] Pagination
- [ ] Detail modal
- [ ] Export (CSV, Excel)

**Sprint 4.2 - CRUD Operations (Analyst+)**
- [ ] Create incident form
- [ ] Edit incident form
- [ ] Delete confirmation
- [ ] Form validation
- [ ] API integration

**Deliverable:** Complete data management

---

### Phase 5: Admin & Monitoring (Week 9)

**Sprint 5.1 - Admin Pages**
- [ ] User management table
- [ ] Role assignment
- [ ] Audit log viewer
- [ ] System settings

**Sprint 5.2 - Monitoring Dashboard**
- [ ] Pipeline status display
- [ ] Data quality metrics
- [ ] System resources
- [ ] Worker status
- [ ] Manual trigger controls

**Deliverable:** Admin capabilities

---

### Phase 6: Polish & Optimization (Week 10)

**Sprint 6.1 - UX Refinement**
- [ ] Loading states
- [ ] Error boundaries
- [ ] Empty states
- [ ] Skeleton loaders
- [ ] Toast notifications

**Sprint 6.2 - Performance & Testing**
- [ ] Code splitting
- [ ] Bundle optimization
- [ ] Accessibility audit
- [ ] E2E test coverage
- [ ] Performance testing
- [ ] Bug fixes

**Deliverable:** Production-ready application

---

## Success Metrics

### User Adoption
- Monthly active users
- Registration conversion rate
- Feature usage rates
- Session duration

### Performance
- Page load times
- API response times
- Error rates
- Uptime percentage

### Business Value
- Data accuracy improvements
- Report generation efficiency
- User satisfaction scores
- Platform citations/references

---

## Future Enhancements (Post-MVP)

### Phase 7: Advanced Features
- Real-time updates (WebSockets)
- Collaborative annotations
- Custom report builder
- Scheduled reports
- Email notifications
- API key management
- Data export automation

### Phase 8: Mobile App
- React Native app
- Offline mode
- Push notifications
- Camera for evidence upload

### Phase 9: AI/ML Enhancements
- Natural language queries
- Automated event extraction
- Image analysis (social media)
- Sentiment analysis dashboard

---

## Appendix

### Technology Stack Summary

**Frontend:**
- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- SWR (data fetching)
- Recharts (visualizations)
- Mapbox GL JS (maps)
- React Hook Form (forms)
- Zod (validation)

**Backend (Already Implemented):**
- FastAPI
- PostgreSQL + PostGIS
- Redis
- Celery
- SQLAlchemy
- Prophet, ARIMA (forecasting)

**Infrastructure:**
- Vercel (frontend hosting)
- Railway (backend + database)
- GitHub (version control)
- GitHub Actions (CI/CD)

### API Endpoint Reference

**Base URL:** `https://naija-conflict-tracker-production.up.railway.app`

**Key Endpoints:**
- Auth: `/api/v1/auth/*`
- Conflicts: `/api/v1/conflicts`
- Analytics: `/api/v1/analytics/*`
- Forecasts: `/api/v1/forecasts/*`
- Spatial: `/api/v1/spatial/*`
- Timeseries: `/api/v1/timeseries/*`
- Monitoring: `/api/v1/monitoring/*`
- Public: `/api/v1/public/*`
- Dashboard: `/api/dashboard/*`

**Full Documentation:** `/docs` (Swagger UI)

---

## Conclusion

This UI wireframe proposal provides a comprehensive, production-ready design for the Nextier Nigeria Conflict Tracker platform. The design leverages the robust backend capabilities while maintaining best practices in:

- **Security:** Role-based access, secure authentication
- **Performance:** Optimized data loading, caching strategies
- **Accessibility:** WCAG 2.1 AA compliance
- **Responsiveness:** Mobile-first design
- **Scalability:** Modular component architecture

The phased implementation roadmap ensures incremental delivery of value while maintaining code quality and user experience standards.

**Next Steps:**
1. Review and approve wireframe proposal
2. Create high-fidelity mockups (Figma)
3. Begin Phase 1 implementation
4. Establish design review cadence
5. Plan user testing sessions

---

**Document Version:** 1.0  
**Last Updated:** January 27, 2026  
**Author:** GitHub Copilot (AI Assistant)  
**Reviewers:** [To be assigned]
