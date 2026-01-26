# Landing Page UI Improvements - Intelligence Dashboard

**Status:** APPROVED & IN PROGRESS  
**Created:** 2026-01-25  
**Author:** AI Assistant  
**Priority:** HIGH

## Executive Summary

Transform the NNVCD landing page from a static summary to a **tactical intelligence terminal** that demonstrates predictive capabilities and correlation analysis between economic factors, climate stress, and violent conflict.

## Core Requirements

### 1. Map Rendering Fix (COMPLETED ✅)
- Fixed height container (600px)
- Proper z-index layering
- Error boundaries for fallback

### 2. Dark Mode Intelligence Aesthetic (COMPLETED ✅)
- Background: `#09090b` (near-black)
- Primary accent: `#ff4b4b` (signal red)
- Severity-coded gradients for KPIs
- Glow effects on hover

### 3. Economic Correlation Visualization (IN PROGRESS)

**Chart Type:** Dual-Axis Line Chart  
**Purpose:** Prove the correlation between macroeconomic indicators and violence spikes

**Left Y-Axis:** Violent Incidents (count)  
**Right Y-Axis:** Fuel Price / Inflation Index (%)  
**X-Axis:** Monthly timeline (last 12 months)

**Data Source:** Historical Excel + Economic API  
**Visual Treatment:**
- Violence line: Red (#ff4b4b)
- Economic line: Orange (#f59e0b)
- Shaded area under violence spikes
- Correlation coefficient displayed

### 4. Climate Stress Heatmap Layer (PLANNED)

**Layer:** Lake Chad Recession Impact  
**Data:** `climate_indicators.geojson`  
**Color Scale:** Brown gradient (desiccation index)  
**Legend Entry:** "Water Recession Index"

**Interactive Features:**
- Hover tooltip shows "Primary Driver: Lake Chad Recession"
- Opacity slider for layer visibility
- Toggle on/off

### 5. Tactical Archetype Bar Chart (PLANNED)

**Chart Type:** Horizontal Bar Chart  
**Purpose:** Show AI categorization accuracy

**Categories:**
- Banditry
- Farmer-Herder Clashes
- Sectarian Insurgency
- Kidnapping
- Cultism
- Resource Conflicts

**Visual Treatment:**
- Bars color-coded by severity
- Count + percentage labels
- Confidence score indicators

## Implementation Plan

### Phase 1: Economic Pulse Chart ⏳
```typescript
// Component: components/landing/EconomicPulseChart.tsx
// Library: Recharts (already installed)
// Data endpoint: /api/v1/public/economic-correlation
```

### Phase 2: Map Enhancement 
```typescript
// Fix: Ensure Nigeria GeoJSON loads
// Add: Climate layer toggle
// Add: Hotspot tooltips with "Primary Driver"
```

### Phase 3: Archetype Visualization
```typescript
// Component: components/landing/ArchetypeChart.tsx
// Data: From landing-stats endpoint
```

## Success Metrics

✅ **Dark Mode Implemented** - High-contrast design with signal red accents  
✅ **Severity Coding** - Red (critical), Orange (high), Blue (medium), Green (low)  
✅ **Trend Indicators** - Up/down arrows with percentages  
🔄 **Map Renders** - Nigeria boundaries visible (currently showing "No data")  
⏳ **Economic Chart** - Dual-axis correlation visualization  
⏳ **Archetype Chart** - AI categorization breakdown  
⏳ **Climate Layer** - GeoJSON overlay with legend

## Technical Decisions

**Chart Library:** Recharts (lightweight, React-native, TypeScript support)  
**Map Library:** react-simple-maps (SVG-based, reliable)  
**Animation:** framer-motion (already in use)  
**Color System:** Tailwind CSS with custom dark theme

## Data Requirements

### Backend API Updates Needed:

```python
# /api/v1/public/landing-stats (ENHANCED)
{
  "total_incidents_30d": 57,
  "total_fatalities_30d": 196,
  "active_hotspots": 0,
  "states_affected": 19,
  
  # NEW: Trend data
  "trends": {
    "incidents_change_pct": 12.5,
    "fatalities_change_pct": 8.3,
    "hotspots_change_pct": -2.1,
    "states_change": 5.7
  },
  
  # NEW: Economic correlation
  "economic_pulse": [
    {"month": "2025-07", "incidents": 42, "fuel_price": 720, "inflation": 22.5},
    {"month": "2025-08", "incidents": 48, "fuel_price": 750, "inflation": 23.1},
    // ... 12 months
  ],
  
  # NEW: Archetype breakdown
  "archetypes": [
    {"type": "Banditry", "count": 23, "percentage": 40.4, "confidence": 0.92},
    {"type": "Farmer-Herder", "count": 15, "percentage": 26.3, "confidence": 0.88},
    {"type": "Sectarian", "count": 12, "percentage": 21.1, "confidence": 0.85},
    {"type": "Kidnapping", "count": 7, "percentage": 12.3, "confidence": 0.90}
  ],
  
  # EXISTING
  "timeline_sparkline": [12, 15, 18, 14, 19, 23],
  "top_states": [...]
}
```

## UI Components Architecture

```
LandingPage
├── Header (dark theme) ✅
├── Hero (NNVCD logo) ✅
├── TacticalKPIGrid ✅
│   ├── StatCard (critical) - Incidents
│   ├── StatCard (high) - Fatalities
│   ├── StatCard (medium) - Hotspots
│   └── StatCard (low) - States
├── EconomicPulseChart (NEW) ⏳
├── MapVisualization
│   ├── NigeriaMap (fix rendering) 🔄
│   └── ClimateLayer (NEW) ⏳
├── ArchetypeChart (NEW) ⏳
└── Features Section ✅
```

## Next Steps

1. ✅ Dark mode theme implemented
2. ✅ Severity-coded KPI cards with trends
3. 🔄 **Fix map "No data" issue** - Ensure GeoJSON loads
4. ⏳ **Build EconomicPulseChart component**
5. ⏳ **Update backend API** with economic/archetype data
6. ⏳ **Add ArchetypeChart component**
7. ⏳ **Integrate climate layer**

---

**Last Updated:** 2026-01-25 20:45 UTC  
**Status:** Phase 1 complete, moving to Economic Pulse Chart
