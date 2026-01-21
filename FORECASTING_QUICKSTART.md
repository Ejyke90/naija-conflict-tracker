# Quick Start: Advanced Forecasting

## 🚀 Start the API Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

## 📊 Test the Endpoints

### 1. Prophet Forecast for Borno State

```bash
curl "http://localhost:8000/api/v1/forecasts/advanced/Borno?location_type=state&model=prophet&weeks_ahead=4"
```

**Expected Response:**
```json
{
  "location": "Borno",
  "model": "prophet",
  "forecast": [
    {
      "date": "2026-01-28",
      "predicted_incidents": 12.3,
      "lower_bound": 8.5,
      "upper_bound": 16.7
    }
  ],
  "metadata": {
    "trend_direction": "decreasing",
    "significant_changepoints": [...]
  }
}
```

---

### 2. Compare All Models

```bash
curl "http://localhost:8000/api/v1/forecasts/compare-models/Kaduna?location_type=state&weeks_ahead=4"
```

Shows Prophet vs ARIMA vs Ensemble side-by-side.

---

### 3. Evaluate Model Performance

```bash
curl "http://localhost:8000/api/v1/forecasts/models/evaluation?state=Borno&test_size=12"
```

Returns MAE, RMSE, MAPE, Coverage metrics for each model.

---

## 📈 Frontend Integration

Use this in your Next.js components:

```typescript
// Fetch forecast
const response = await fetch(
  'http://localhost:8000/api/v1/forecasts/advanced/Borno?location_type=state&model=prophet'
);
const data = await response.json();

// Display with Recharts
<LineChart data={data.forecast}>
  <Line dataKey="predicted_incidents" />
  <Area 
    dataKey="lower_bound" 
    dataKey2="upper_bound"
    fill="rgba(0,0,255,0.1)"
  />
</LineChart>
```

---

## 🔧 Troubleshooting

**Issue:** `ModuleNotFoundError: No module named 'prophet'`

**Solution:**
```bash
pip install prophet statsmodels
```

**Issue:** "Insufficient data" error

**Solution:** Model needs at least 10 weeks of historical data. Try a different state (Borno, Kaduna, Plateau have the most data).

---

## 📚 Full Documentation

See [ADVANCED_FORECASTING.md](./ADVANCED_FORECASTING.md) for complete details.
