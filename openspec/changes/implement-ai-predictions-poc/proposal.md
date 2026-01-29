# Implement AI Predictions PoC for Dashboard

## Why
The dashboard has a placeholder "AI Predictions" component that shows no actual predictions. The backend has forecasting models (Prophet, ARIMA, Ensemble) implemented but they are not exposed to the frontend. Users need to see meaningful AI-powered conflict predictions to understand platform capabilities.

## What Changes
- Create `/api/v1/predictions/next-30-days` endpoint that returns predictions for top at-risk states
- Build responsive dashboard component showing upcoming conflict risk predictions
- Integrate with existing forecasting backend (Prophet/Ensemble models)
- Display predictions with accuracy metrics and confidence intervals
- Real-time updates for top 5 at-risk states

## Scope: PoC/MVP Only
- **NOT** a production-scale system
- **Focus:** Demonstrate prediction capability with high accuracy
- **Target:** Top 5 states showing highest conflict risk in next 30 days
- **Accuracy Target:** 75%+ MAPE (Mean Absolute Percentage Error)
- **Scale:** Minimal - just enough to prove the concept

## Success Criteria
- Dashboard shows next 30-day predictions for top 5 states
- Predictions include: estimated incidents, fatalities, risk level (Low/Medium/High/Critical)
- Confidence intervals displayed (90% CI)
- Accuracy metrics shown: model type, MAPE, last training date
- Real-time prediction updates (refresh every 6 hours)
- Mobile responsive design