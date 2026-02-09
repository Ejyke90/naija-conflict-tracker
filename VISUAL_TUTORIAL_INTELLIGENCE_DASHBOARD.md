# Visual Tutorial: Dynamic State Comparison Feature

## Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                    Nigeria Conflict Intelligence Platform              │
│                                                                         │
│  Frontend (Next.js/React)          Backend (FastAPI)      Database     │
│  ┌──────────────────┐              ┌───────────────┐    ┌──────────┐  │
│  │ Analytics Page   │              │ TimeSeries    │    │PostgreSQL│  │
│  │  /analytics      │              │   API         │    │ +PostGIS │  │
│  └────────┬─────────┘              └───────┬───────┘    └─────┬────┘  │
│           │                                 │                  │        │
│           ▼                                 │                  │        │
│  ┌──────────────────────────────────┐      │                  │        │
│  │ StateComparisonChart Component   │      │                  │        │
│  ├──────────────────────────────────┤      │                  │        │
│  │ Props:                           │      │                  │        │
│  │  - states: string[]              │      │                  │        │
│  │  - monthsBack: number            │      │                  │        │
│  │  - maxStates: number (new!)      │      │                  │        │
│  │  - allowUserSelection: boolean   │      │                  │        │
│  ├──────────────────────────────────┤      │                  │        │
│  │ State:                           │      │                  │        │
│  │  - selectedStates (dynamic)      │      │                  │        │
│  │  - selectedMonths (dynamic)      │      │                  │        │
│  │  - showControls (toggle panel)   │      │                  │        │
│  └──────────┬───────────────────────┘      │                  │        │
│             │                               │                  │        │
│             │  GET /api/v1/timeseries/      │                  │        │
│             │  trend-comparison?            │                  │        │
│             │  states=Borno,Kaduna&         │                  │        │
│             │  months_back=12               │                  │        │
│             └──────────────────────────────►│                  │        │
│                                             │                  │        │
│                                             │  SQL Query       │        │
│                                             ├─────────────────►│        │
│                                             │  (monthly agg)   │        │
│                                             │                  │        │
│                                             │  ◄────────────── │        │
│                                             │  Results         │        │
│                ◄────────────────────────────┤                  │        │
│                JSON Response                │                  │        │
│                                             │                  │        │
│  ┌──────────────────────────────────┐      │                  │        │
│  │ Chart Rendered (Recharts)        │      │                  │        │
│  │  - Line Chart (trends)           │      │                  │        │
│  │  - Bar Chart (totals)            │      │                  │        │
│  │  - Summary Cards                 │      │                  │        │
│  │  - Detailed Table                │      │                  │        │
│  └──────────────────────────────────┘      │                  │        │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

## User Interface Flow

### Before Configuration Panel
```
┌──────────────────────────────────────────────────────────────┐
│ 📍 State Comparison                           [⚙️ Configure] │
│ Comparing 5 states over 12 months (up to 5 states supported)│
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  [Trends] [Totals]  │  [Incidents] [Fatalities]             │
│                                                               │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐│
│  │ Borno   │ │ Zamfara │ │ Kaduna  │ │ Plateau │ │ Niger  ││
│  │ ● 345   │ │ ● 234   │ │ ● 187   │ │ ● 156   │ │ ● 98   ││
│  │ 28.8/mo │ │ 19.5/mo │ │ 15.6/mo │ │ 13.0/mo │ │ 8.2/mo ││
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └────────┘│
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              Line Chart (Trends View)                  │  │
│  │  100 ┤                                          ╱─●    │  │
│  │   80 ┤                     ╱─●──●──●──●───●───●       │  │
│  │   60 ┤        ╱──●───●──●──                           │  │
│  │   40 ┤    ╱──●                                        │  │
│  │   20 ┤  ●                                             │  │
│  │    0 └──┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬─  │  │
│  │        Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec│  │
│  │        — Borno  — Zamfara  — Kaduna  — Plateau — Niger│  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### After Clicking "⚙️ Configure"
```
┌──────────────────────────────────────────────────────────────┐
│ 📍 State Comparison                           [⚙️ Configure] │
│ Comparing 3 states over 18 months (up to 5 states supported)│
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │
│ ┃ ⚙️ Comparison Settings                                   ┃ │
│ ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫ │
│ ┃ Time Period                                              ┃ │
│ ┃ [6 months] [12 months] [18 months]● [24 months]         ┃ │
│ ┃                                                          ┃ │
│ ┃ Select States (max 5) - Currently: 3                    ┃ │
│ ┃ ┌──────────────────────────────────────────────────┐    ┃ │
│ ┃ │ [Abia] [Adamawa] [Borno✓] [Kaduna✓] [Lagos✓]    │    ┃ │
│ ┃ │ [Niger] [Plateau] [Rivers] [Zamfara] [Yobe]     │    ┃ │
│ ┃ │ [Delta] [Edo] [Kano] [Sokoto] [Taraba] ...      │    ┃ │
│ ┃ └──────────────────────────────────────────────────┘    ┃ │
│ ┃ 💡 Click states to add/remove. Green = selected         ┃ │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │
│                                                               │
│  [Trends]● [Totals]  │  [Incidents]● [Fatalities]           │
│                                                               │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                        │
│  │ Borno   │ │ Kaduna  │ │ Lagos   │                        │
│  │ ● 523   │ │ ● 298   │ │ ● 156   │                        │
│  │ 29.1/mo │ │ 16.6/mo │ │ 8.7/mo  │                        │
│  └─────────┘ └─────────┘ └─────────┘                        │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              Line Chart Updated (18 months)            │  │
│  │  ...                                                   │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## State Selection Logic

### Visual State Transitions

```
┌──────────────────────────────────────────────────────────────┐
│                  State Button States                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Unselected (Available)                                      │
│  ┌────────┐                                                  │
│  │ Lagos  │  ← Click to SELECT                              │
│  └────────┘                                                  │
│  Light gray, border, hover effect                           │
│                                                               │
│  Selected (Active)                                           │
│  ┌────────┐                                                  │
│  │ Lagos✓ │  ← Click to DESELECT                            │
│  └────────┘                                                  │
│  Green background, shadow, white text                        │
│                                                               │
│  Disabled (Max Reached)                                      │
│  ┌────────┐                                                  │
│  │ Kano   │  ← Cannot click (already at 5 states)           │
│  └────────┘                                                  │
│  Gray, no border, cursor disabled                            │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Selection Rules

```
┌────────────────────────────────────────────────────────┐
│ Current: 3 states selected (Borno, Kaduna, Lagos)     │
│ Max: 5 states                                          │
├────────────────────────────────────────────────────────┤
│                                                        │
│ Action: Click "Plateau" (unselected)                  │
│ ✅ ALLOWED → Now 4 states selected                    │
│                                                        │
│ Action: Click "Niger" (unselected)                    │
│ ✅ ALLOWED → Now 5 states selected (MAX REACHED)      │
│                                                        │
│ Action: Click "Zamfara" (unselected)                  │
│ ❌ BLOCKED → Already at max (5 states)                │
│ → Button disabled, gray color                         │
│                                                        │
│ Action: Click "Borno" (selected)                      │
│ ✅ ALLOWED → Now 4 states selected                    │
│ → "Zamfara" becomes available again                   │
│                                                        │
│ Action: Deselect all until 1 state left              │
│ → Try to click last state (e.g., "Lagos")            │
│ ❌ BLOCKED → Minimum 1 state required                 │
│                                                        │
└────────────────────────────────────────────────────────┘
```

## Data Transformation Pipeline

### API Response Structure
```json
{
  "comparison": {
    "Borno": {
      "months": ["2024-01", "2024-02", "2024-03", ...],
      "incidents": [23, 19, 31, ...],
      "fatalities": [67, 45, 89, ...],
      "total": 345,
      "avgPerMonth": 28.8
    },
    "Kaduna": { ... },
    "Lagos": { ... }
  },
  "timeRange": "12 months",
  "generatedAt": "2025-02-08T..."
}
```

### Chart Data Transformation

```javascript
// Original API response
{
  "Borno": { months: ["2024-01", "2024-02"], incidents: [23, 19] },
  "Kaduna": { months: ["2024-01", "2024-02"], incidents: [15, 22] }
}

// Transformed for Recharts (Line Chart)
[
  { month: "2024-01", Borno: 23, Kaduna: 15 },
  { month: "2024-02", Borno: 19, Kaduna: 22 }
]

// Transformed for Bar Chart (Totals)
[
  { state: "Borno", total: 345, avgPerMonth: 28.8 },
  { state: "Kaduna", total: 234, avgPerMonth: 19.5 }
]
```

## Component Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│ 1. Component Mount                                      │
│    ├─ Initialize state with props                      │
│    │   selectedStates = states.slice(0, maxStates)     │
│    │   selectedMonths = monthsBack                     │
│    └─ Trigger useEffect (fetch data)                   │
├─────────────────────────────────────────────────────────┤
│ 2. Data Fetch (useEffect)                              │
│    ├─ Build API URL with parameters                    │
│    ├─ Fetch from /api/v1/timeseries/trend-comparison   │
│    ├─ Handle response/errors                           │
│    └─ Update state: setData(result)                    │
├─────────────────────────────────────────────────────────┤
│ 3. User Interaction                                     │
│    ├─ Click "⚙️ Configure" → setShowControls(true)     │
│    ├─ Select time period → setSelectedMonths(18)       │
│    ├─ Toggle state → toggleStateSelection("Lagos")     │
│    └─ Changes trigger useEffect → Re-fetch data        │
├─────────────────────────────────────────────────────────┤
│ 4. Re-render                                            │
│    ├─ Transform new data for charts                    │
│    ├─ Update summary cards                             │
│    ├─ Redraw charts (Recharts)                         │
│    └─ Update table with new trends                     │
└─────────────────────────────────────────────────────────┘
```

## Intelligence Insights Component Flow

```
┌─────────────────────────────────────────────────────────┐
│ IntelligenceInsights Component                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Fetches: /api/v1/intelligence/archetypes               │
│  ↓                                                      │
│ Returns:                                                │
│  {                                                      │
│    summary: {                                           │
│      "Banditry": {                                      │
│        total_incidents: 87,                             │
│        total_fatalities: 143,                           │
│        avg_fatalities_per_incident: 1.64,               │
│        percentage: 35.2                                 │
│      },                                                 │
│      "Farmer-Herder": { ... },                          │
│      "Terrorism": { ... }                               │
│    }                                                    │
│  }                                                      │
│  ↓                                                      │
│ Display:                                                │
│  ┌────────────────────────────────────────────┐       │
│  │ 🛡️ Conflict Intelligence & Archetypes      │       │
│  │ 12 months                                  │       │
│  ├────────────────────────────────────────────┤       │
│  │ Comprehensive intelligence analysis:       │       │
│  │ Security risk scoring, conflict            │       │
│  │ archetypes, state snapshots, and           │       │
│  │ predictive threat assessments across       │       │
│  │ 247 verified incidents                     │       │
│  ├────────────────────────────────────────────┤       │
│  │                                             │       │
│  │ ┌─────────────┐ ┌─────────────┐           │       │
│  │ │ 🚨 Banditry │ │ 💧 Farmer-  │           │       │
│  │ │ 35.2%       │ │   Herder    │           │       │
│  │ │ 87 incidents│ │ 28.4%       │           │       │
│  │ │ 143 deaths  │ │ 70 incidents│           │       │
│  │ │ Severity:   │ │ 56 deaths   │           │       │
│  │ │ Medium      │ │ Severity:   │           │       │
│  │ └─────────────┘ │ Low         │           │       │
│  │                 └─────────────┘           │       │
│  │                                             │       │
│  │ 💡 Key Insights:                            │       │
│  │ • Banditry is dominant (35.2%)             │       │
│  │ • 2 archetypes show high lethality        │       │
│  │ • Monitor seasonal Farmer-Herder triggers │       │
│  └────────────────────────────────────────────┘       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Complete User Journey

```
┌──────────────────────────────────────────────────────────┐
│ Step 1: User visits /analytics page                     │
│         ↓                                                │
│ Step 2: Page loads StateComparisonChart component       │
│         Default: 5 states, 12 months                    │
│         ↓                                                │
│ Step 3: User clicks "⚙️ Configure"                      │
│         → Configuration panel opens                     │
│         ↓                                                │
│ Step 4: User selects 18 months                          │
│         → selectedMonths = 18                           │
│         → useEffect triggers                            │
│         → Fetches new data                              │
│         ↓                                                │
│ Step 5: User clicks "Lagos" state                       │
│         → toggleStateSelection("Lagos")                 │
│         → selectedStates = [..., "Lagos"]               │
│         → useEffect triggers again                      │
│         → Fetches updated comparison                    │
│         ↓                                                │
│ Step 6: Chart updates with new data                     │
│         → Shows 6 states over 18 months                 │
│         → Summary cards reflect new states              │
│         → Line chart redraws with 18-month data         │
│         ↓                                                │
│ Step 7: User toggles to "Totals" view                   │
│         → setViewMode('totals')                         │
│         → Bar chart displays instead of line chart      │
│         ↓                                                │
│ Step 8: User switches to "Fatalities" metric            │
│         → setMetric('fatalities')                       │
│         → Charts update to show deaths instead          │
│         ↓                                                │
│ Step 9: User analyzes trends and insights               │
│         → Reviews trend arrows in table                 │
│         → Identifies highest-risk states                │
│         → Makes data-driven decisions                   │
└──────────────────────────────────────────────────────────┘
```

## Key Takeaways

### ✅ What We Built

1. **Dynamic Configuration**
   - User-selectable states (up to 5)
   - Configurable time periods (6/12/18/24 months)
   - Real-time chart updates

2. **Enhanced Intelligence Description**
   - Security risk scoring
   - State snapshots
   - Predictive assessments
   - Conflict archetypes

3. **Improved UX**
   - Visual state indicators (green/gray)
   - Helpful tooltips
   - Clear limits and constraints
   - Responsive design

### 🎯 User Benefits

- ✅ **Flexibility**: Compare any states, any time period
- ✅ **Clarity**: Understand what the platform does (not just charts)
- ✅ **Control**: Configure analysis to specific needs
- ✅ **Insights**: Better regional conflict pattern analysis

### 🔧 Technical Achievements

- ✅ **React State Management**: Complex multi-state interactions
- ✅ **API Integration**: Dynamic parameter passing
- ✅ **UI Components**: Reusable, configurable components
- ✅ **Data Transformation**: API → Chart data pipeline
- ✅ **Error Handling**: Graceful failures, loading states

---

**Next**: Test the implementation at `/analytics` → State Comparison section!
