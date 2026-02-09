# 🚀 Quick Reference: Dynamic Intelligence Dashboard

## 📋 What Changed

### 1. IntelligenceInsights Component
- ✅ Updated description to show full platform capabilities
- ✅ Now mentions: Security risk scoring, state snapshots, predictive assessments

### 2. StateComparisonChart Component
- ✅ Default states: 3 → **5** (Borno, Zamfara, Kaduna, Plateau, Niger)
- ✅ **New**: User can select states dynamically (max 5)
- ✅ **New**: User can choose time period (6/12/18/24 months)
- ✅ **New**: Configuration panel with "⚙️ Configure" button
- ✅ **New**: Visual state selection with color feedback

---

## 🎮 How to Use

### Basic Usage (Analytics Page)

1. Navigate to: `http://localhost:3000/analytics`
2. Scroll to "State Comparison" section
3. Click **"⚙️ Configure"** button
4. Select time period (6/12/18/24 months)
5. Click states to add/remove (green = selected)
6. Watch chart update in real-time!

### Component Usage (Developers)

```tsx
import StateComparisonChart from '@/components/charts/StateComparisonChart';

// Default (5 states, 12 months, controls enabled)
<StateComparisonChart />

// Custom configuration
<StateComparisonChart 
  states={['Lagos', 'Kano', 'Rivers']}
  monthsBack={6}
  maxStates={3}
  allowUserSelection={true}
/>

// Locked comparison (no user controls)
<StateComparisonChart 
  states={['Borno', 'Zamfara']}
  monthsBack={24}
  allowUserSelection={false}
/>
```

---

## 🎨 UI Controls

### Configuration Panel

```
⚙️ Comparison Settings

Time Period
[6 months] [12 months]● [18 months] [24 months]

Select States (max 5) - Currently: 3
┌────────────────────────────────────┐
│ [Abia] [Adamawa] [Borno✓] [Kaduna✓]│
│ [Lagos✓] [Niger] [Plateau] ...     │
└────────────────────────────────────┘
💡 Click states to add/remove
```

### Button States

- **Selected**: Green background, white text, shadow
- **Unselected**: Light gray, border, hover effect
- **Disabled**: Gray, no hover (max limit reached)

### View Modes

- **Trends** (Line Chart) - Show monthly progression
- **Totals** (Bar Chart) - Compare aggregate numbers

### Metrics

- **Incidents** (Blue theme) - Number of conflict events
- **Fatalities** (Red theme) - Number of deaths

---

## 🔧 Technical Details

### New Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `maxStates` | `number` | `5` | Maximum states allowed |
| `allowUserSelection` | `boolean` | `true` | Enable/disable configure panel |

### State Variables

```tsx
selectedStates: string[]      // User-selected states
selectedMonths: number        // User-selected time period
showControls: boolean         // Toggle config panel visibility
```

### Functions

```tsx
toggleStateSelection(state: string)
// Adds/removes state from selection
// Enforces: min 1 state, max maxStates
```

---

## 🧪 Test Checklist

- [ ] Page loads with 5 default states
- [ ] "⚙️ Configure" button opens panel
- [ ] Time period selector works (6/12/18/24)
- [ ] Can add states (green highlight)
- [ ] Can remove states (returns to gray)
- [ ] Max limit enforced (disables unselected)
- [ ] Minimum 1 state (can't remove last)
- [ ] Chart updates after changes
- [ ] Trends/Totals toggle works
- [ ] Incidents/Fatalities toggle works

---

## 📊 API Integration

**Endpoint**: `/api/v1/timeseries/trend-comparison`

**Parameters**:
- `states`: Comma-separated (e.g., "Borno,Kaduna,Lagos")
- `months_back`: 6-36 (default: 12)

**Response**:
```json
{
  "comparison": {
    "Borno": {
      "months": ["2024-01", ...],
      "incidents": [23, ...],
      "total": 345,
      "avgPerMonth": 28.8
    }
  }
}
```

---

## 🎯 User Scenarios

### Scenario 1: Compare Top Conflict States
1. Click "⚙️ Configure"
2. Select: Borno, Zamfara, Kaduna, Plateau, Niger
3. Choose: 12 months
4. View: Trends (line chart)
5. Metric: Incidents

### Scenario 2: Analyze Southern Nigeria
1. Click "⚙️ Configure"
2. Deselect all northern states
3. Select: Lagos, Rivers, Delta
4. Choose: 6 months
5. View: Totals (bar chart)
6. Metric: Fatalities

### Scenario 3: Long-term Analysis
1. Click "⚙️ Configure"
2. Select: Borno, Yobe (terrorism hotspots)
3. Choose: 24 months
4. View: Trends
5. Toggle between Incidents/Fatalities

---

## 📁 Files Modified

1. `frontend/components/intelligence/IntelligenceInsights.tsx`
   - Line 137: Updated description text

2. `frontend/components/charts/StateComparisonChart.tsx`
   - Lines 30-34: New props interface
   - Lines 43-88: State management + available states list
   - Lines 90-132: Updated useEffect + toggleStateSelection
   - Lines 149-155: Dynamic description
   - Lines 157-170: Configure button
   - Lines 174-225: Configuration panel UI

---

## 🚨 Known Limits

- **Max States**: 5 (enforced client + server)
- **Min States**: 1 (can't deselect last)
- **Time Range**: 6-24 months (UI), 6-36 months (API)
- **Available States**: 37 Nigerian states + FCT

---

## 🔮 Future Enhancements

### Phase 2 (Optional)
- [ ] Save preferences to localStorage
- [ ] Quick presets ("Top 5", "Southern States")
- [ ] Export data (CSV/Excel)
- [ ] Auto-generated insights
- [ ] Forecast integration (next 3 months)

### Phase 3 (Advanced)
- [ ] State metadata (population, area)
- [ ] Normalized metrics (per 100k pop)
- [ ] Statistical correlation tests
- [ ] Custom date ranges (calendar picker)

---

## ✅ Summary

**What Works**:
- ✅ Dynamic state selection (1-5 states)
- ✅ Configurable time periods (6/12/18/24 months)
- ✅ Interactive UI with visual feedback
- ✅ Real-time chart updates
- ✅ Enhanced intelligence descriptions

**Testing Status**: ✅ No TypeScript errors

**Ready for**: ✅ Local testing at `/analytics`

---

**Need Help?** See:
- [INTELLIGENCE_DASHBOARD_UPGRADE.md](INTELLIGENCE_DASHBOARD_UPGRADE.md) - Full implementation details
- [VISUAL_TUTORIAL_INTELLIGENCE_DASHBOARD.md](VISUAL_TUTORIAL_INTELLIGENCE_DASHBOARD.md) - Visual diagrams and flows
