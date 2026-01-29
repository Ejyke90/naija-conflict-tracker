# Design Document: AI Predictions PoC

## Architecture Overview

### Backend Architecture
```
┌─────────────────────────────────────────┐
│   GET /api/v1/predictions/next-30-days  │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│   PredictionController                   │
│  - Query top 5 at-risk states            │
│  - Call forecasting models               │
│  - Format response                       │
└────────────┬────────────────────────────┘
             │
      ┌──────┴──────┐
      ▼             ▼
┌───────────┐  ┌──────────────────┐
│ PostgreSQL│  │ Redis Cache      │
│ Conflicts │  │ (predictions)    │
└───────────┘  └──────────────────┘
      │
      ▼
┌─────────────────────────────────────────┐
│ EnsembleForecaster (Prophet + ARIMA)    │
│ - forecast(state, weeks_ahead=4)        │
│ - Returns: predictions, CI, MAPE        │
└─────────────────────────────────────────┘
```

### Frontend Architecture
```
┌──────────────────────────────────────────┐
│   Dashboard (ConflictDashboard.tsx)      │
│   - Calls Analytics tab                  │
└────────────┬─────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────┐
│   AIPredictions.tsx (New)                │
│   - Fetch from API using SWR             │
│   - Display 5 prediction cards           │
│   - Show risk levels, confidence        │
│   - 6-hour auto-refresh                 │
└────────────┬─────────────────────────────┘
             │
      ┌──────┴──────────────┐
      ▼                     ▼
┌─────────────────┐  ┌──────────────────┐
│ PredictionCard  │  │ MetricsDisplay   │
│ (per state)     │  │ (accuracy, etc)  │
└─────────────────┘  └──────────────────┘
```

## Data Flow

### 1. Initial Load
1. Dashboard mounts, AIPredictions component loads
2. Component uses SWR hook: `useSWR('/api/v1/predictions/next-30-days', fetcher, { revalidateInterval: 6*60*60*1000 })`
3. API endpoint queried
4. Backend queries PostgreSQL for top 5 at-risk states (last 30 days data)
5. For each state, EnsembleForecaster generates 4-week forecast
6. Results cached in Redis for 6 hours
7. Response sent to frontend
8. Component displays prediction cards

### 2. Real-Time Updates
- SWR automatically refetches every 6 hours
- User can click "Refresh" button for manual refresh
- Last updated timestamp shown

## Risk Assessment

### Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Forecaster models fail silently | High | Add error logging, return error status in API, show error toast |
| No data for newly added states | Medium | Query only states with 10+ incidents in last 6 months |
| Redis cache miss causes slow response | Low | Cache predictions for 6 hours, sync with forecasting task schedule |
| Inaccurate predictions damage credibility | High | Show MAPE on UI, include "Experimental" label, document limitations |
| API timeout with many forecasts | Medium | Run forecasts asynchronously via Celery task, cache results |

### Performance Considerations
- **Caching:** Redis caches predictions for 6 hours (matches Celery task schedule)
- **Async:** Backend forecasts run in Celery tasks daily at 2 AM (not blocking API)
- **Frontend:** SWR handles caching, minimal re-renders
- **Load:** Only 5 states forecasted, minimal database queries

## Testing Strategy

### Unit Tests
- `test_get_top_at_risk_states()` - Verify correct states selected
- `test_format_prediction_response()` - Check JSON structure
- `test_confidence_interval_calculation()` - Validate CI math

### Integration Tests
- Test full flow: Query DB → Forecast → Return JSON
- Test error cases: No data, missing model, timeout
- Test caching: Verify Redis stores/retrieves predictions

### Validation Tests
- Compare forecasts vs actual incidents from past month
- Calculate MAPE for each state
- Document accuracy metrics

## Future Improvements (Not in PoC)
1. **Risk Level Classification**: ML model to predict incident type (communal, insurgency, etc.)
2. **Contributing Factors**: Show which factors (poverty, unemployment) drive predictions
3. **Scenario Analysis**: "What if" analysis for policy makers
4. **Historical Accuracy**: Track prediction accuracy over time
5. **Geographic Granularity**: Drill down to LGA level (currently state-level only)
6. **Model Selection**: Allow users to choose between Prophet, ARIMA, Ensemble
7. **Retraining Pipeline**: Automated model retraining when new data arrives
8. **Comparison View**: Side-by-side comparison of model predictions