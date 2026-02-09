# Conflict Forecast Page - Feature Specification

**Status**: Draft  
**Created**: 2026-02-08  
**Type**: Feature Addition  
**Impact**: High - New dedicated forecast visualization page  

---

## Overview

Transform the current "3-Month Forecast" section into a **dedicated, immersive forecast page** with rich visualizations inspired by weather forecast apps. Keep a teaser section on the landing page that routes users to the full forecast experience.

---

## Design Inspiration

Based on:
- **Numeric Weather Forecast** (dark theme, location selection, multi-metric cards, hourly charts, forecast tables)
- **Weather Forecasting Web App** (hero visual, storm forecast, probability metrics, city comparison)
- **Gyaan Forecast Overview** (revenue trends, confidence intervals, comparison views, activity history)

---

## Current State

**Landing Page Section**:
```tsx
{/* 3-Month Forecast (Linear Trend) */}
<section>
  <h3>📈 3-Month Forecast (Linear Trend)</h3>
  <LineChart ... />
</section>
```

**Issues**:
- ❌ Limited space for detailed visualizations
- ❌ No interactive state/region selection
- ❌ No confidence intervals or probability indicators
- ❌ Missing model comparison (Prophet, ARIMA, LSTM)
- ❌ No historical accuracy metrics
- ❌ Can't drill down into specific forecasts

---

## Proposed Solution

### **1. Dedicated Forecast Page** (`/forecasts`)

#### **A. Page Layout**

```
┌─────────────────────────────────────────────────────────┐
│ HEADER: Nigeria Conflict Forecasting                   │
│ "AI-powered conflict incident predictions"             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ HERO SECTION (Dark gradient background)        │   │
│ │                                                 │   │
│ │ Select Region/State: [Borno ▼]  Period: [3M ▼] │   │
│ │                                                 │   │
│ │  Current Month Summary                          │   │
│ │  ┌─────────┐ ┌─────────┐ ┌─────────┐          │   │
│ │  │  87     │ │  +12%   │ │  92%    │          │   │
│ │  │Incidents│ │vs Last  │ │Accuracy │          │   │
│ │  │         │ │Month    │ │         │          │   │
│ │  └─────────┘ └─────────┘ └─────────┘          │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ MAIN FORECAST CHART                             │   │
│ │ ┌─────────────────────────────────────────────┐ │   │
│ │ │                                             │ │   │
│ │ │  200─┐                                      │ │   │
│ │ │      │     Historical ─────┬─── Forecast   │ │   │
│ │ │  150─┤                     │                │ │   │
│ │ │      │   ●●●●●●●●●●●●●●   │  ○○○○○○○      │ │   │
│ │ │  100─┤                  ●●●┴●●              │ │   │
│ │ │      │                    (confidence)      │ │   │
│ │ │   50─┤                                      │ │   │
│ │ │      └─────────────────────────────────────  │ │   │
│ │ │       Jan Feb Mar Apr May Jun Jul Aug Sep   │ │   │
│ │ │                                             │ │   │
│ │ │  Legend: ● Actual  ○ Predicted  ░ 95% CI  │ │   │
│ │ └─────────────────────────────────────────────┘ │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ MODEL COMPARISON                                │   │
│ │ ┌──────────┐ ┌──────────┐ ┌──────────┐        │   │
│ │ │ Prophet  │ │  ARIMA   │ │   LSTM   │        │   │
│ │ │  MAE: 8.2│ │ MAE: 9.1 │ │ MAE: 7.5 │        │   │
│ │ │  [View] │ │  [View]  │ │  [View]  │        │   │
│ │ └──────────┘ └──────────┘ └──────────┘        │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ NEXT 12 WEEKS - DETAILED FORECAST               │   │
│ │ ┌─────────────────────────────────────────────┐ │   │
│ │ │Week │Date Range │Predicted│Confidence│Risk │ │   │
│ │ │─────┼───────────┼─────────┼──────────┼─────│ │   │
│ │ │ 1   │Feb 9-15   │  23     │  89%     │🟡   │ │   │
│ │ │ 2   │Feb 16-22  │  28     │  85%     │🟠   │ │   │
│ │ │ 3   │Feb 23-29  │  31     │  82%     │🟠   │ │   │
│ │ │ 4   │Mar 1-7    │  25     │  78%     │🟡   │ │   │
│ │ │...                                          │ │   │
│ │ └─────────────────────────────────────────────┘ │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ STATE COMPARISON                                │   │
│ │ Compare forecast across states:                 │   │
│ │ [Borno] [Zamfara] [Kaduna] [+ Add State]       │   │
│ │                                                 │   │
│ │ ┌─────────────────────────────────────────────┐ │   │
│ │ │  Multi-line chart showing 3-month forecasts │ │   │
│ │ │  for selected states with different colors  │ │   │
│ │ └─────────────────────────────────────────────┘ │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ FORECAST INSIGHTS & ALERTS                      │   │
│ │                                                 │   │
│ │ ⚠️ Borno: Spike predicted in Week 2 (+45%)     │   │
│ │ 📈 Plateau: Upward trend detected (3 weeks)    │   │
│ │ ✅ Rivers: Declining trend continues           │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ FORECAST HISTORY                                │   │
│ │ Last updated: 2 days ago by AI System          │   │
│ │                                                 │   │
│ │ • Feb 6: Updated Borno forecast to 87 incidents│   │
│ │ • Feb 3: LSTM model retrained with new data    │   │
│ │ • Jan 30: Accuracy improved to 92% (Prophet)   │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### **2. Landing Page Teaser Section**

Replace the current full forecast chart with a **teaser card**:

```tsx
{/* Forecast Teaser */}
<section className="bg-gradient-to-br from-purple-900 to-blue-900 rounded-xl p-8 text-white">
  <div className="flex items-center justify-between">
    <div>
      <h3 className="text-2xl font-bold mb-2">
        📈 AI-Powered Conflict Forecasting
      </h3>
      <p className="text-purple-200 mb-4">
        Predict incidents up to 3 months ahead with 92% accuracy
      </p>
      
      {/* Mini preview chart */}
      <div className="h-32 bg-white/10 rounded-lg mb-4">
        <MiniSparklineChart data={previewData} />
      </div>
      
      {/* Quick stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div>
          <p className="text-sm text-purple-200">Next Week</p>
          <p className="text-xl font-bold">23 incidents</p>
        </div>
        <div>
          <p className="text-sm text-purple-200">Trend</p>
          <p className="text-xl font-bold">↑ +12%</p>
        </div>
        <div>
          <p className="text-sm text-purple-200">Confidence</p>
          <p className="text-xl font-bold">89%</p>
        </div>
      </div>
    </div>
    
    <div className="text-right">
      <Link href="/forecasts">
        <button className="bg-white text-purple-900 px-6 py-3 rounded-lg font-semibold hover:bg-purple-100 transition-all">
          View Full Forecast →
        </button>
      </Link>
    </div>
  </div>
</section>
```

---

### **3. Technical Implementation**

#### **A. File Structure**

```
frontend/
├── pages/
│   └── forecasts.tsx              ← New forecast page
├── components/
│   └── forecasts/
│       ├── ForecastHero.tsx       ← Header with state selector
│       ├── ForecastMainChart.tsx  ← Main prediction chart
│       ├── ModelComparison.tsx    ← Prophet/ARIMA/LSTM cards
│       ├── WeeklyForecastTable.tsx← 12-week detailed table
│       ├── StateComparison.tsx    ← Multi-state forecast
│       ├── ForecastInsights.tsx   ← AI-generated alerts
│       └── ForecastHistory.tsx    ← Update timeline
└── lib/
    └── forecast-api.ts            ← API client for forecasts
```

#### **B. API Endpoints**

**Existing** (from `backend/app/api/v1/endpoints/predictions.py`):
- `GET /api/v1/predictions/forecast?state={state}&weeks={weeks}`

**New Endpoints Needed**:
```python
# GET /api/v1/predictions/forecast/detailed
@router.get("/forecast/detailed")
async def get_detailed_forecast(
    state: str = Query(...),
    weeks: int = Query(12, ge=1, le=52),
    model: str = Query("prophet", enum=["prophet", "arima", "lstm", "ensemble"]),
    db: Session = Depends(get_db)
):
    """
    Returns:
    {
        "state": "Borno",
        "model": "prophet",
        "historical": {
            "dates": ["2025-11-01", ...],
            "actual": [45, 52, ...],
        },
        "forecast": {
            "dates": ["2026-02-09", ...],
            "predicted": [23, 28, 31, ...],
            "lower_bound": [18, 22, 25, ...],
            "upper_bound": [28, 34, 37, ...],
            "confidence": [0.89, 0.85, 0.82, ...]
        },
        "metrics": {
            "mae": 8.2,
            "rmse": 10.5,
            "accuracy": 0.92
        },
        "insights": [
            "Spike predicted in Week 2 (+45%)",
            "Upward trend detected"
        ]
    }
    """

# GET /api/v1/predictions/forecast/compare
@router.get("/forecast/compare")
async def compare_state_forecasts(
    states: str = Query(..., description="Comma-separated states"),
    weeks: int = Query(12),
    db: Session = Depends(get_db)
):
    """
    Returns multi-state forecast comparison
    """

# GET /api/v1/predictions/forecast/history
@router.get("/forecast/history")
async def get_forecast_history(
    limit: int = Query(10),
    db: Session = Depends(get_db)
):
    """
    Returns forecast update timeline
    """
```

---

### **4. UI Components Breakdown**

#### **A. ForecastHero Component**

```tsx
interface ForecastHeroProps {
  selectedState: string;
  onStateChange: (state: string) => void;
  currentMonthSummary: {
    incidents: number;
    change: number;
    accuracy: number;
  };
}

export function ForecastHero({ ... }: ForecastHeroProps) {
  return (
    <div className="bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 rounded-xl p-8 text-white">
      {/* State selector */}
      <div className="mb-6">
        <label>Select Region/State</label>
        <Select value={selectedState} onChange={onStateChange}>
          <option>All Nigeria</option>
          <option>Borno</option>
          <option>Zamfara</option>
          {/* ... */}
        </Select>
      </div>
      
      {/* Current month cards */}
      <div className="grid grid-cols-3 gap-4">
        <MetricCard 
          label="Incidents This Month"
          value={incidents}
          icon={<Activity />}
        />
        <MetricCard 
          label="vs Last Month"
          value={`${change > 0 ? '+' : ''}${change}%`}
          icon={<TrendingUp />}
          trend={change > 0 ? 'up' : 'down'}
        />
        <MetricCard 
          label="Model Accuracy"
          value={`${accuracy}%`}
          icon={<Target />}
        />
      </div>
    </div>
  );
}
```

#### **B. ForecastMainChart Component**

```tsx
export function ForecastMainChart({ forecastData }: Props) {
  return (
    <div className="bg-white rounded-lg p-6 shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold">12-Week Forecast</h3>
        
        {/* Model selector */}
        <div className="flex gap-2">
          <button className={modelType === 'prophet' ? 'active' : ''}>
            Prophet
          </button>
          <button className={modelType === 'arima' ? 'active' : ''}>
            ARIMA
          </button>
          <button className={modelType === 'lstm' ? 'active' : ''}>
            LSTM
          </button>
          <button className={modelType === 'ensemble' ? 'active' : ''}>
            Ensemble
          </button>
        </div>
      </div>
      
      {/* Chart */}
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={combinedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          {/* Historical actual */}
          <Line 
            type="monotone" 
            dataKey="actual" 
            stroke="#3b82f6" 
            strokeWidth={2}
            dot={{ r: 4 }}
            name="Historical"
          />
          
          {/* Forecast */}
          <Line 
            type="monotone" 
            dataKey="predicted" 
            stroke="#8b5cf6" 
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={{ r: 4, fill: '#8b5cf6', strokeWidth: 2, stroke: '#fff' }}
            name="Forecast"
          />
          
          {/* Confidence interval */}
          <Area 
            type="monotone"
            dataKey="upper"
            stroke="none"
            fill="#8b5cf6"
            fillOpacity={0.1}
          />
          <Area 
            type="monotone"
            dataKey="lower"
            stroke="none"
            fill="#8b5cf6"
            fillOpacity={0.1}
          />
        </LineChart>
      </ResponsiveContainer>
      
      {/* Legend */}
      <div className="mt-4 flex gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-600 rounded"></div>
          <span>Historical Actual</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 border-2 border-purple-600 border-dashed rounded"></div>
          <span>AI Forecast</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-purple-600/20 rounded"></div>
          <span>95% Confidence Interval</span>
        </div>
      </div>
    </div>
  );
}
```

#### **C. WeeklyForecastTable Component**

```tsx
export function WeeklyForecastTable({ weeks }: Props) {
  return (
    <div className="bg-white rounded-lg p-6 shadow-lg">
      <h3 className="text-xl font-bold mb-4">Next 12 Weeks - Detailed Forecast</h3>
      
      <table className="w-full">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left">Week</th>
            <th className="px-4 py-3 text-left">Date Range</th>
            <th className="px-4 py-3 text-right">Predicted</th>
            <th className="px-4 py-3 text-right">Range</th>
            <th className="px-4 py-3 text-center">Confidence</th>
            <th className="px-4 py-3 text-center">Risk</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {weeks.map((week, index) => (
            <tr key={index} className="hover:bg-gray-50">
              <td className="px-4 py-3 font-medium">{index + 1}</td>
              <td className="px-4 py-3 text-sm text-gray-600">
                {week.dateRange}
              </td>
              <td className="px-4 py-3 text-right font-bold">
                {week.predicted}
              </td>
              <td className="px-4 py-3 text-right text-sm text-gray-600">
                {week.lower} - {week.upper}
              </td>
              <td className="px-4 py-3 text-center">
                <Badge variant={week.confidence > 0.85 ? 'success' : 'warning'}>
                  {(week.confidence * 100).toFixed(0)}%
                </Badge>
              </td>
              <td className="px-4 py-3 text-center">
                <RiskIndicator level={week.riskLevel} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

---

### **5. Color Scheme (Inspired by Designs)**

```css
/* Primary (Purple gradient - forecast theme) */
--forecast-primary: #6366f1;    /* Indigo */
--forecast-dark: #4c1d95;       /* Purple-900 */
--forecast-accent: #8b5cf6;     /* Purple-500 */

/* Secondary (Green - positive trends) */
--forecast-success: #10b981;    /* Emerald-500 */
--forecast-warning: #f59e0b;    /* Amber-500 */
--forecast-danger: #ef4444;     /* Red-500 */

/* Backgrounds */
--forecast-bg-gradient: linear-gradient(135deg, #4c1d95 0%, #1e3a8a 100%);
--forecast-card-bg: #ffffff;
--forecast-card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
```

---

### **6. Routing Configuration**

**Update `frontend/pages/forecasts.tsx`**:

```tsx
import { GetStaticProps } from 'next';
import ForecastPage from '@/components/forecasts/ForecastPage';

export default ForecastPage;

export const getStaticProps: GetStaticProps = async () => {
  // Pre-fetch Nigeria-wide forecast for SSG
  const res = await fetch('http://localhost:8000/api/v1/predictions/forecast/detailed?state=Nigeria&weeks=12');
  const initialData = await res.json();
  
  return {
    props: {
      initialData
    },
    revalidate: 3600 // Revalidate every hour
  };
};
```

---

### **7. Success Metrics**

**User Engagement**:
- ✅ Time on forecast page: >2 minutes avg
- ✅ State comparison usage: >40% of visitors
- ✅ Model comparison clicks: >25% of visitors
- ✅ Landing page teaser CTR: >15%

**Technical Performance**:
- ✅ Initial page load: <2 seconds
- ✅ Chart render time: <500ms
- ✅ API response time: <300ms
- ✅ SSG regeneration: <1 minute

---

### **8. Implementation Phases**

#### **Phase 1: Foundation** (Week 1)
- [ ] Create `/forecasts` page route
- [ ] Build ForecastHero component
- [ ] Build ForecastMainChart with basic line chart
- [ ] Update landing page with teaser section
- [ ] Test routing

#### **Phase 2: Core Features** (Week 2)
- [ ] Add confidence intervals to chart
- [ ] Build WeeklyForecastTable component
- [ ] Implement model comparison (Prophet/ARIMA/LSTM)
- [ ] Add state selector functionality
- [ ] Create API endpoints for detailed forecasts

#### **Phase 3: Advanced Features** (Week 3)
- [ ] Build StateComparison multi-line chart
- [ ] Add ForecastInsights (AI alerts)
- [ ] Implement ForecastHistory timeline
- [ ] Add export functionality (PDF, CSV)
- [ ] Polish UI/UX

#### **Phase 4: Optimization** (Week 4)
- [ ] Implement caching (Redis)
- [ ] Add loading states and skeletons
- [ ] Optimize chart performance
- [ ] Mobile responsiveness
- [ ] Accessibility audit
- [ ] User testing

---

### **9. Migration Path**

**Before** (Landing page):
```tsx
<section>
  <h3>📈 3-Month Forecast</h3>
  <LineChart data={forecastData} />
</section>
```

**After** (Landing page teaser):
```tsx
<ForecastTeaser 
  nextWeekPrediction={23}
  trend={+12}
  confidence={89}
  onClick={() => router.push('/forecasts')}
/>
```

**New** (Dedicated page):
```
/forecasts
  - Full immersive experience
  - All features detailed above
```

---

### **10. Decisions Made**

1. **Model Selection**: ✅ Default to "Ensemble" model, allow users to switch to individual models (Prophet, ARIMA, LSTM) via toggle buttons
2. **Confidence Threshold**: ⚠️ Warning triggered when confidence <80%, amber badge shown
3. **Export Format**: ✅ PDF report with forecast chart, metrics table, and insights
4. **Real-time Updates**: ✅ WebSocket integration for live forecast updates when new data arrives
5. **Historical Comparison**: ✅ Show "Forecast vs Actual" accuracy chart over time (last 6 months)

---

## Acceptance Criteria

- [ ] Dedicated `/forecasts` page accessible via navigation
- [ ] Landing page shows teaser with mini preview + CTA button
- [ ] Hero section with state selector and current month metrics
- [ ] Main forecast chart with historical + predicted data
- [ ] Confidence intervals displayed as shaded area
- [ ] Model comparison cards (Prophet, ARIMA, LSTM)
- [ ] 12-week detailed forecast table
- [ ] State comparison multi-line chart
- [ ] AI-generated insights and alerts
- [ ] Forecast history timeline
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Page loads in <2 seconds
- [ ] SSG with hourly revalidation

---

## References

- **Weather Forecast UIs**: Dark themes, metric cards, probability charts, location selection
- **Business Forecast Dashboards**: Confidence intervals, model comparison, activity history
- **Current Implementation**: `frontend/components/landing/MonthlyTrendChart.tsx`
- **Prediction API**: `backend/app/api/v1/endpoints/predictions.py`

---

**Next Steps**: Review and approve this spec, then begin Phase 1 implementation.
