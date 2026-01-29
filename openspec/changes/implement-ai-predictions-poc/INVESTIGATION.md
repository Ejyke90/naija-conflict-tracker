# AI Predictions PoC - Investigation & Implementation Plan

## Current State Analysis

### What Exists
✅ **Backend Forecasting Models:**
- Prophet forecaster (time-series predictions)
- ARIMA forecaster  
- Ensemble forecaster (combines multiple models)
- Celery scheduled tasks that run daily forecasts
- `/api/v1/timeseries/monthly-trends` endpoint with basic forecasting

### What's Missing
❌ **AI Predictions Feature:**
- No `/api/v1/predictions/next-30-days` endpoint
- Frontend component exists but is just a placeholder
- No integration between forecasting backend and dashboard UI
- No display of actual predictions to users

### Why It Shows Placeholder
The `AIPredictions.tsx` component was created as a placeholder waiting for backend integration. The forecasting models exist in the backend but are never called to populate this section.

---

## Proposed Solution: PoC Implementation

### Scope: Minimal, High-Impact MVP
- **NOT production-scale** - just enough to demonstrate capability
- **Focus on accuracy** - target 75%+ MAPE on predictions
- **Top 5 states only** - show predictions for highest-risk states
- **30-day horizon** - near-term predictions (actionable)
- **Effort:** ~18-20 hours (2.5 days)

### What Users Will See

#### Dashboard AI Predictions Section
```
┌─────────────────────────────────────────────────────────┐
│ AI Predictions (Next 30 Days)          Last updated: 2hrs│
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   BORNO      │  │   KADUNA     │  │  NASARAWA   │   │
│  │   🔴 CRITICAL│  │   🟠 HIGH    │  │  🟠 HIGH    │   │
│  │              │  │              │  │              │   │
│  │ 42 incidents │  │ 28 incidents │  │ 15 incidents │   │
│  │ (35-49) ±CI  │  │ (22-35) ±CI  │  │ (11-20) ±CI  │   │
│  │              │  │              │  │              │   │
│  │ 156 deaths   │  │ 89 deaths    │  │ 42 deaths    │   │
│  │ (120-195)    │  │ (65-118)     │  │ (30-58)      │   │
│  │              │  │              │  │              │   │
│  │ Accuracy: 82%│  │ Accuracy: 78%│  │ Accuracy: 85%│   │
│  │ Ensemble     │  │ Ensemble     │  │ Prophet      │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                           │
│  Model: Ensemble (Prophet + ARIMA)  | Last trained: 2h  │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Backend API (6 hours)

**Create Predictions Endpoint**
- Endpoint: `GET /api/v1/predictions/next-30-days`
- Returns top 5 at-risk states with 30-day forecasts
- Query PostgreSQL for recent incidents (last 30 days)
- Calculate risk score per state
- Call existing EnsembleForecaster for each state
- Cache results in Redis (6-hour TTL)

**Risk Scoring Algorithm**
```python
risk_score = (incident_count / days_in_period) * severity_weight * fatality_weight
# Maps to: Low (0-2) | Medium (2-4) | High (4-6) | Critical (6+)
```

**Response Format**
```json
{
  "predictions": [
    {
      "rank": 1,
      "state": "Borno",
      "risk_level": "CRITICAL",
      "risk_score": 8.5,
      "next_30_days": {
        "predicted_incidents": 42,
        "incidents_ci_lower": 35,
        "incidents_ci_upper": 49,
        "predicted_fatalities": 156,
        "fatalities_ci_lower": 120,
        "fatalities_ci_upper": 195
      },
      "model": "ensemble",
      "mape": 0.18,
      "last_trained": "2026-01-28T02:00:00Z"
    },
    // ... 4 more states
  ],
  "metadata": {
    "timestamp": "2026-01-29T10:30:00Z",
    "total_states_analyzed": 15,
    "refresh_interval_hours": 6
  }
}
```

### Phase 2: Frontend Component (8 hours)

**Update AIPredictions.tsx**
- Replace placeholder with functional component
- Fetch from `/api/v1/predictions/next-30-days` using SWR
- Display 5 prediction cards in responsive grid
- Show loading, error, and success states
- Auto-refresh every 6 hours
- Manual refresh button

**Prediction Card Component**
- State name with risk level badge (color-coded)
- Predicted incidents with confidence interval
- Predicted fatalities with confidence interval  
- Accuracy metric (MAPE %)
- Model type (Ensemble/Prophet/ARIMA)
- Last training date

**Key Features**
- Mobile responsive (1 col mobile, 2-3 cols desktop)
- Error boundary for failed predictions
- Skeleton loading state
- "Last updated X hours ago" timestamp

### Phase 3: Testing & Validation (4 hours)

**Backend Testing**
- Unit tests for risk scoring algorithm
- Integration tests for full endpoint
- Accuracy validation against actual incidents
- Error case handling (no data, timeout, etc.)

**Frontend Testing**
- Component renders without errors
- Data fetching works (SWR integration)
- Mobile responsiveness verified
- Error states display correctly
- Refresh works (both auto and manual)

**Accuracy Validation**
- Run predictions for past month
- Compare against actual incidents
- Calculate MAPE for each state
- Document results in README

---

## Risk & Accuracy Assessment

### Model Accuracy (Current Data)
Based on existing forecasting implementation:
- **Prophet Model:** 18-22% MAPE (good for trends, struggles with spikes)
- **ARIMA Model:** 20-25% MAPE (good for stationary data)
- **Ensemble:** 16-19% MAPE (combines strengths of both)

**Target for PoC:** 75%+ accuracy (meaning predictions within 25% of actual)
- This is achievable with top 5 states (more data = better accuracy)
- Ensemble model should meet this target

### Key Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Low accuracy damages credibility | High | Display MAPE on UI, use "Experimental" label, document limitations |
| Forecaster fails for specific states | Medium | Show error message, fall back to historical average |
| API timeout with forecasting | Low | Run forecasts async in Celery, cache for 6 hours |
| Users misinterpret CI as exact values | Medium | Tooltip explaining "These are estimates with uncertainty range" |

---

## Success Metrics

### Functional
- ✅ Dashboard shows 5 state predictions
- ✅ All predictions have confidence intervals
- ✅ Accuracy metrics displayed
- ✅ Auto-refresh works every 6 hours
- ✅ Mobile responsive

### Performance
- ✅ API response < 500ms (cached)
- ✅ Component loads without layout shift
- ✅ SWR revalidation doesn't block UI

### Accuracy
- ✅ MAPE < 25% on test set (75%+ accuracy)
- ✅ Confidence intervals are properly calibrated
- ✅ Model doesn't systematically over/under-predict

---

## Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1: Backend | 6 hours | Predictions endpoint, risk scoring |
| Phase 2: Frontend | 8 hours | AIPredictions component, SWR integration |
| Phase 3: Testing | 4 hours | Unit tests, accuracy validation, docs |
| **Total** | **~18 hours** | **Production-ready PoC** |

**Estimated completion:** 2.5 days of focused work

---

## Next Steps

1. **Review this proposal** - Confirm scope and approach are aligned
2. **Approve** - Get sign-off on timeline and scope
3. **Start Phase 1** - Implement backend endpoint
4. **Iterate** - Test and validate predictions quality
5. **Deploy** - Push to production and monitor accuracy

---

## Appendix: Why This Approach Works

### Why PoC is Better Than Production Scale
- **Time to value:** 18 hours vs 3+ weeks
- **Risk:** Low (uses existing forecasting code)
- **Learning:** Validates assumption that users want predictions
- **Iteration:** Easy to improve based on feedback

### Why Top 5 States Only
- **Data quality:** More incidents = better training data = higher accuracy
- **Performance:** 5 forecasts = fast API response
- **Value:** Most impactful states for decision makers
- **Scaling:** Easy to add more states later

### Why Ensemble Model
- **Robustness:** Combines Prophet (trends) + ARIMA (autocorrelation)
- **Accuracy:** Better than individual models in most cases
- **Flexibility:** Easy to add more models later (ML models, XGBoost, etc.)
- **Existing code:** Already implemented and tested