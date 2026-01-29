# Implementation Plan for AI Predictions PoC

## Phase 1: Backend API Development (Days 1-2)

### Task 1.1: Create Predictions Endpoint
- [ ] Create `/app/routes/predictions.py`
- [ ] Endpoint: `GET /api/v1/predictions/next-30-days`
- [ ] Returns: Top 5 at-risk states with 30-day predictions
- [ ] Include: incidents forecast, fatalities forecast, confidence intervals

### Task 1.2: Query Top At-Risk States
- [ ] Query last 30 days of incidents
- [ ] Calculate risk score = (incident_count / days) * 10
- [ ] Sort states by risk score descending
- [ ] Select top 5 states

### Task 1.3: Generate Forecasts
- [ ] For each of top 5 states, call EnsembleForecaster.forecast(state, weeks_ahead=4)
- [ ] Extract: predictions, confidence intervals, MAPE
- [ ] Format response with metadata: model_type, last_trained, accuracy

## Phase 2: Frontend Component (Days 2-3)

### Task 2.1: Create Predictions Component
- [ ] Replace AIPredictions.tsx placeholder with functional component
- [ ] Fetch from `/api/v1/predictions/next-30-days`
- [ ] Display predictions in card layout

### Task 2.2: Display Predictions Cards
- [ ] Each state gets a card showing:
  - State name + risk level badge (Low/Medium/High/Critical)
  - Predicted incidents (next 30 days)
  - Predicted fatalities (next 30 days)
  - Confidence interval (90% CI) as error bars
  - MAPE accuracy metric (e.g., "85% accuracy")

### Task 2.3: Styling & Responsiveness
- [ ] Use Tailwind CSS grid (responsive: 1 col mobile, 2-3 cols desktop)
- [ ] Color code risk levels: Green/Yellow/Orange/Red
- [ ] Add loading state with spinner
- [ ] Add error state with retry button

### Task 2.4: Real-Time Updates
- [ ] Use SWR hook with 6-hour refresh interval
- [ ] Show "Last updated: X hours ago" timestamp
- [ ] Manual refresh button

## Phase 3: Testing & Validation (Days 3-4)

### Task 3.1: Backend Testing
- [ ] Test predictions endpoint returns valid JSON
- [ ] Verify all 5 top states included
- [ ] Check confidence intervals are reasonable (e.g., ±15%)
- [ ] Test error handling (no data, missing model)

### Task 3.2: Frontend Testing
- [ ] Verify component renders without errors
- [ ] Test loading, error, and success states
- [ ] Check mobile responsiveness
- [ ] Verify SWR data fetching works

### Task 3.3: Accuracy Validation
- [ ] Compare forecasts vs actual incidents from past month
- [ ] Calculate MAPE for all states
- [ ] Document accuracy metrics in README

## Deliverables

### Code
- [ ] `/app/routes/predictions.py` - Backend API
- [ ] Updated `AIPredictions.tsx` - Frontend component
- [ ] Unit tests for predictions endpoint

### Documentation
- [ ] API endpoint documentation (request/response examples)
- [ ] Accuracy metrics and model information
- [ ] How to interpret predictions and confidence intervals
- [ ] Known limitations and future improvements

### Example Response

```json
{
  "timestamp": "2026-01-29T10:30:00Z",
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
    {
      "rank": 2,
      "state": "Kaduna",
      "risk_level": "HIGH",
      "risk_score": 6.2,
      "next_30_days": {
        "predicted_incidents": 28,
        "incidents_ci_lower": 22,
        "incidents_ci_upper": 35,
        "predicted_fatalities": 89,
        "fatalities_ci_lower": 65,
        "fatalities_ci_upper": 118
      },
      "model": "ensemble",
      "mape": 0.22,
      "last_trained": "2026-01-28T02:00:00Z"
    }
  ],
  "metadata": {
    "total_states_analyzed": 15,
    "top_states_returned": 5,
    "refresh_interval_hours": 6,
    "accuracy_note": "MAPE = Mean Absolute Percentage Error (lower is better)"
  }
}
```

## Effort Estimate
- Backend: 6 hours
- Frontend: 8 hours  
- Testing: 4 hours
- **Total: ~18 hours (2.5 days)**

## Dependencies
- Existing Prophet/ARIMA models in backend (already implemented)
- Redis cache for caching predictions
- PostgreSQL with conflict data (already populated)