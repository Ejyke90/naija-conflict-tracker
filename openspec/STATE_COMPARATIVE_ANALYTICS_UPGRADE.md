# State Comparative Analytics & Intelligent Forecasting - Feature Upgrade

**Status:** Proposal  
**Priority:** High  
**Agents:** @DATA_SCIENCE_AGENT @STATISTICIAN_AGENT @TIMESERIES_AGENT @API_AGENT @DATAVIZ_AGENT  
**Created:** 2026-02-08

---

## Current Implementation Review

### Existing "Conflicts by State" Component
**Location:** [frontend/src/components/dashboard/StateAnalysis.tsx](../frontend/src/components/dashboard/StateAnalysis.tsx)

**Current Capabilities:**
- ✅ Basic bar charts (incidents & fatalities by state)
- ✅ Static hardcoded sample data
- ✅ Simple risk level classification (High/Medium/Low)
- ✅ Tabular state statistics

**Limitations:**
- ❌ No real-time API integration
- ❌ No forecasting integration
- ❌ No comparative trend analysis
- ❌ No statistical significance testing
- ❌ No anomaly detection
- ❌ No predictive risk scoring
- ❌ No correlation analysis with external factors

---

## Proposed Intelligent Reporting Framework

### 1. **Multi-Dimensional State Comparison**

#### A. Enhanced Metrics Dashboard
Expand beyond simple counts to comprehensive conflict intelligence:

```typescript
interface StateComparativeMetrics {
  // Historical Performance (Last 12 months)
  totalIncidents: number;
  fatalityRate: number;
  civilianImpactScore: number;      // Weighted: kidnappings + displaced + civilian deaths
  conflictIntensityTrend: TrendDirection;  // ↑ Escalating, → Stable, ↓ De-escalating
  
  // Predictive Metrics (Next 30 days)
  forecastedIncidents: number;
  forecastConfidence: number;        // 0-100% model confidence
  riskLevel: 'Critical' | 'High' | 'Medium' | 'Low';
  riskChangeVsPrevious: number;      // % change from last period
  
  // Comparative Rankings
  incidentRank: number;              // 1-37 among Nigerian states
  fatalityRank: number;
  improvementRank: number;           // States showing most improvement
  
  // Statistical Insights
  volatility: number;                // Variance in monthly incidents
  seasonalityScore: number;          // 0-1: How seasonal are conflicts?
  anomalyCount: number;              // Unusual spikes in last 90 days
  
  // Geospatial Context
  conflictDensity: number;           // Incidents per 1000 km²
  affectedLGAs: number;
  clusteredConflicts: boolean;       // Concentrated vs. dispersed
  
  // Actor Intelligence
  dominantActorGroups: string[];
  actorDiversity: number;            // Number of unique armed groups
  crossBorderActivity: boolean;      // Conflicts near state boundaries
}
```

#### B. Statistical Comparison Engine
**Implementation:** Python/SciPy + Statsmodels

```python
# backend/app/services/state_comparative_analytics.py

from scipy.stats import mannwhitneyu, kruskal, spearmanr
from statsmodels.tsa.stattools import adfuller
import numpy as np

class StateComparativeAnalyzer:
    """
    Statistical comparison of conflict patterns across states
    """
    
    def compare_states_pairwise(self, state_a: str, state_b: str) -> dict:
        """
        Compare two states using Mann-Whitney U test
        Returns: p-value, effect_size, interpretation
        """
        incidents_a = self._get_monthly_incidents(state_a)
        incidents_b = self._get_monthly_incidents(state_b)
        
        stat, p_value = mannwhitneyu(incidents_a, incidents_b, alternative='two-sided')
        
        # Calculate effect size (rank-biserial correlation)
        n1, n2 = len(incidents_a), len(incidents_b)
        effect_size = 1 - (2*stat) / (n1 * n2)
        
        return {
            "state_a": state_a,
            "state_b": state_b,
            "p_value": p_value,
            "statistically_significant": p_value < 0.05,
            "effect_size": effect_size,
            "interpretation": self._interpret_comparison(p_value, effect_size)
        }
    
    def rank_states_by_multiple_criteria(self) -> list:
        """
        Multi-criteria ranking using weighted composite score
        """
        states = self._get_all_states()
        rankings = []
        
        for state in states:
            # Fetch metrics
            incidents = self._get_total_incidents(state)
            fatalities = self._get_total_fatalities(state)
            trend = self._calculate_trend_slope(state)
            volatility = self._calculate_volatility(state)
            
            # Composite score (lower is better)
            composite_score = (
                0.3 * self._normalize(incidents) +      # 30% weight on volume
                0.4 * self._normalize(fatalities) +     # 40% weight on fatalities
                0.2 * self._normalize(volatility) +     # 20% weight on unpredictability
                0.1 * max(0, trend)                     # 10% penalty for increasing trends
            )
            
            rankings.append({
                "state": state,
                "composite_score": composite_score,
                "metrics": {
                    "incidents": incidents,
                    "fatalities": fatalities,
                    "trend_slope": trend,
                    "volatility": volatility
                }
            })
        
        return sorted(rankings, key=lambda x: x['composite_score'], reverse=True)
    
    def detect_state_clusters(self) -> dict:
        """
        Group states with similar conflict patterns using K-means
        """
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        
        # Feature matrix: [incidents, fatalities, trend, seasonality, volatility]
        features = self._build_state_feature_matrix()
        
        # Normalize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Cluster into 4 groups: Critical, High-Risk, Medium-Risk, Stable
        kmeans = KMeans(n_clusters=4, random_state=42)
        cluster_labels = kmeans.fit_predict(features_scaled)
        
        # Map clusters to risk categories
        return self._assign_cluster_labels(cluster_labels, features)
```

---

### 2. **Advanced Forecasting Integration**

#### A. State-Level Predictive Models
**Proven Algorithms to Implement:**

##### **Prophet Model** (Already Implemented ✅)
- **Strengths:** Handles seasonality, missing data, trend changepoints
- **Use Case:** Long-term trends (3-6 months)
- **Enhancement:** Add state-specific seasonality patterns (e.g., farming seasons, religious periods)

```python
# Enhanced Prophet configuration for Nigerian context
from prophet import Prophet

model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=False,
    daily_seasonality=False,
    seasonality_mode='multiplicative',  # Better for conflict data
    changepoint_prior_scale=0.05,       # Conservative trend changes
    seasonality_prior_scale=10.0        # Flexible seasonality
)

# Add Nigerian-specific holidays/events
nigeria_events = pd.DataFrame({
    'holiday': ['Eid_al_Fitr', 'Eid_al_Adha', 'Christmas', 'Elections'],
    'ds': pd.to_datetime(['2025-04-01', '2025-06-08', '2025-12-25', '2027-02-01']),
    'lower_window': -7,
    'upper_window': 7
})
model.add_country_holidays(country_name='NG')
```

##### **ARIMA Model** (Already Implemented ✅)
- **Strengths:** Short-term accuracy, captures autocorrelation
- **Use Case:** Next 2-4 weeks predictions
- **Enhancement:** Auto ARIMA with seasonal differencing

```python
from pmdarima import auto_arima

# Automatic order selection
model = auto_arima(
    y=monthly_incidents,
    seasonal=True,
    m=12,                    # Monthly seasonality
    stepwise=True,
    suppress_warnings=True,
    error_action='ignore',
    trace=False
)
```

##### **New: LSTM Neural Network** 📊
- **Strengths:** Captures complex non-linear patterns
- **Use Case:** States with erratic patterns (e.g., Zamfara, Kaduna)

```python
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

def build_lstm_forecaster(lookback_window=12):
    """
    LSTM model for conflict forecasting
    """
    model = Sequential([
        LSTM(50, activation='relu', return_sequences=True, 
             input_shape=(lookback_window, 5)),  # 5 features
        Dropout(0.2),
        LSTM(50, activation='relu'),
        Dropout(0.2),
        Dense(25, activation='relu'),
        Dense(1)  # Predict incidents
    ])
    
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model

# Features: [incidents, fatalities, displaced, armed_groups, neighboring_state_incidents]
```

##### **New: Bayesian Structural Time Series (BSTS)** 📊
- **Strengths:** Quantifies uncertainty, incorporates external regressors
- **Use Case:** Policy impact analysis (e.g., military interventions)

```python
from pybsts import BSTS

# Include poverty rate, military presence as regressors
model = BSTS(
    components=['trend', 'seasonality'],
    regressors=['poverty_rate', 'military_deployment', 'unemployment_rate']
)

forecast = model.fit_predict(
    y=incidents,
    regressors=external_data,
    forecast_horizon=12
)
```

#### B. Ensemble Meta-Model
**Weighted average of all models based on historical accuracy**

```python
class StateConflictEnsemble:
    """
    Combines Prophet, ARIMA, LSTM, and BSTS predictions
    """
    
    def __init__(self):
        self.models = {
            'prophet': ProphetForecaster(),
            'arima': ARIMAForecaster(),
            'lstm': LSTMForecaster(),
            'bsts': BSTSForecaster()
        }
        self.weights = None
    
    def auto_calibrate_weights(self, state: str):
        """
        Calculate optimal model weights based on backtesting
        """
        # Backtest each model on last 6 months
        performance = {}
        for name, model in self.models.items():
            mae = self._backtest_model(model, state, periods=6)
            performance[name] = 1 / mae  # Inverse error as weight
        
        # Normalize weights to sum to 1
        total = sum(performance.values())
        self.weights = {k: v/total for k, v in performance.items()}
        
    def forecast(self, state: str, weeks_ahead: int = 4):
        """
        Generate weighted ensemble forecast
        """
        predictions = {}
        for name, model in self.models.items():
            pred = model.forecast(state=state, weeks_ahead=weeks_ahead)
            predictions[name] = pred
        
        # Weighted combination
        ensemble_forecast = sum(
            self.weights[name] * predictions[name]['yhat']
            for name in self.models.keys()
        )
        
        # Aggregate confidence intervals
        lower = min(p['yhat_lower'] for p in predictions.values())
        upper = max(p['yhat_upper'] for p in predictions.values())
        
        return {
            "state": state,
            "forecast_period": f"{weeks_ahead} weeks",
            "predicted_incidents": ensemble_forecast,
            "confidence_interval": {"lower": lower, "upper": upper},
            "model_weights": self.weights,
            "individual_predictions": predictions
        }
```

---

### 3. **LLM-Enhanced Narrative Reporting** 🤖

#### A. Automated Intelligence Briefings
**Use LLM to generate human-readable state comparisons**

```python
from openai import OpenAI

class ConflictIntelligenceReporter:
    """
    Generate natural language reports using GPT-4
    """
    
    def generate_state_comparison_report(self, state_a: str, state_b: str) -> str:
        """
        Create executive summary comparing two states
        """
        # Gather data
        metrics_a = self._get_state_metrics(state_a)
        metrics_b = self._get_state_metrics(state_b)
        forecast_a = self._get_forecast(state_a)
        forecast_b = self._get_forecast(state_b)
        
        prompt = f"""
        You are a conflict analyst for Nigeria. Generate a concise 2-paragraph 
        executive summary comparing conflict dynamics in {state_a} and {state_b}.
        
        DATA:
        {state_a}:
        - Incidents (last 90 days): {metrics_a['incidents']}
        - Fatalities: {metrics_a['fatalities']}
        - Trend: {metrics_a['trend']}
        - Forecast (next 30 days): {forecast_a['predicted_incidents']} incidents
        
        {state_b}:
        - Incidents (last 90 days): {metrics_b['incidents']}
        - Fatalities: {metrics_b['fatalities']}
        - Trend: {metrics_b['trend']}
        - Forecast (next 30 days): {forecast_b['predicted_incidents']} incidents
        
        Focus on:
        1. Which state faces greater risk and why
        2. Key differences in conflict patterns
        3. Actionable insights for policymakers
        
        Tone: Professional, data-driven, actionable
        """
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3  # Lower temperature for factual reporting
        )
        
        return response.choices[0].message.content
    
    def generate_weekly_state_rankings_report(self) -> str:
        """
        Weekly automated report ranking all states
        """
        rankings = self._get_state_rankings()
        top_5 = rankings[:5]
        improved = self._get_most_improved_states()
        
        prompt = f"""
        Generate a weekly "Nigeria Conflict Risk Assessment" report.
        
        TOP 5 HIGH-RISK STATES:
        {json.dumps(top_5, indent=2)}
        
        MOST IMPROVED STATES (reducing conflict):
        {json.dumps(improved, indent=2)}
        
        Structure:
        1. Executive Summary (2 sentences)
        2. High-Risk States Analysis (3-4 bullets per state)
        3. Positive Developments (states showing improvement)
        4. Week Ahead Forecast (key states to watch)
        
        Include specific numbers and trends.
        """
        
        # Similar LLM call...
```

#### B. Anomaly Explanations
**Use LLM to contextualize unusual spikes**

```python
def explain_anomaly(self, state: str, date: datetime, spike_magnitude: float) -> str:
    """
    Generate explanation for conflict spike
    """
    # Fetch news articles from that period
    news = self._get_news_articles(state, date, days_window=7)
    historical_context = self._get_historical_events(state)
    
    prompt = f"""
    Analyze this conflict spike:
    - State: {state}
    - Date: {date}
    - Magnitude: {spike_magnitude}x normal levels
    
    Recent news headlines:
    {news[:5]}
    
    Historical context:
    {historical_context}
    
    Provide 2-3 sentence explanation for the spike.
    """
    
    # LLM generates: "The spike in Plateau State on May 15 correlates with 
    # escalating farmer-herder clashes following the killing of a local chief. 
    # This follows a pattern of retaliatory violence typical in this region."
```

---

### 4. **Enhanced API Endpoints**

#### New Routes to Implement:

```python
# backend/app/api/v1/endpoints/state_analytics.py

@router.get("/states/comparative-analysis")
async def get_state_comparative_analysis(
    states: List[str] = Query(..., description="2-5 states to compare"),
    time_range: str = Query("12months", pattern="^(3months|6months|12months|24months)$"),
    include_forecast: bool = Query(True),
    include_llm_summary: bool = Query(False),
    db: Session = Depends(get_db)
) -> StateComparativeReport:
    """
    Advanced multi-state comparison with statistical testing
    
    Returns:
    - Side-by-side metrics
    - Statistical significance tests
    - Forecasts for each state
    - Ranking and clustering
    - Optional LLM-generated summary
    """
    pass

@router.get("/states/{state}/intelligence-report")
async def get_state_intelligence_report(
    state: str,
    format: str = Query("json", pattern="^(json|pdf|markdown)$"),
    include_forecast: bool = Query(True),
    db: Session = Depends(get_db)
) -> StateIntelligenceReport:
    """
    Comprehensive state-level intelligence report
    
    Includes:
    - Historical trends (12 months)
    - Forecasts (4 weeks ahead)
    - Anomaly detection
    - Actor analysis
    - Geospatial hotspot mapping
    - LLM-generated executive summary
    - Comparative ranking vs other states
    """
    pass

@router.get("/states/rankings")
async def get_state_rankings(
    ranking_criteria: str = Query(
        "composite",
        pattern="^(composite|incidents|fatalities|improvement|risk_score)$"
    ),
    time_range: str = Query("12months"),
    db: Session = Depends(get_db)
) -> List[StateRanking]:
    """
    Rank all Nigerian states by various criteria
    
    Criteria options:
    - composite: Weighted multi-factor score
    - incidents: Total incident count
    - fatalities: Total fatality count
    - improvement: Most improved (trend direction)
    - risk_score: Predictive risk for next 30 days
    """
    pass

@router.get("/states/{state}/forecast-confidence")
async def get_forecast_confidence_analysis(
    state: str,
    model: str = Query("ensemble", pattern="^(prophet|arima|lstm|ensemble)$"),
    db: Session = Depends(get_db)
) -> ForecastConfidenceReport:
    """
    Detailed forecast confidence analysis
    
    Returns:
    - Model backtesting performance (MAPE, MAE, RMSE)
    - Prediction intervals (50%, 80%, 95%)
    - Model uncertainty sources
    - Recommended confidence level
    """
    pass
```

---

### 5. **Frontend Enhancements**

#### A. Interactive State Comparison Dashboard

```tsx
// frontend/src/components/dashboard/StateComparativeAnalytics.tsx

import { LineChart, BarChart, ScatterChart, HeatMap } from 'recharts';
import { Select, MultiSelect, Toggle, Tabs } from '@/components/ui';

export default function StateComparativeAnalytics() {
  const [selectedStates, setSelectedStates] = useState(['Borno', 'Zamfara', 'Kaduna']);
  const [timeRange, setTimeRange] = useState('12months');
  const [showForecasts, setShowForecasts] = useState(true);
  const [activeTab, setActiveTab] = useState('comparison');
  
  return (
    <div className="space-y-6">
      {/* Control Panel */}
      <Card>
        <CardHeader>
          <CardTitle>State Comparison Settings</CardTitle>
        </CardHeader>
        <CardContent className="flex gap-4">
          <MultiSelect 
            label="Select States (2-5)"
            options={nigerianStates}
            value={selectedStates}
            onChange={setSelectedStates}
            max={5}
          />
          <Select
            label="Time Range"
            options={['3months', '6months', '12months', '24months']}
            value={timeRange}
            onChange={setTimeRange}
          />
          <Toggle
            label="Include Forecasts"
            checked={showForecasts}
            onChange={setShowForecasts}
          />
        </CardContent>
      </Card>
      
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="comparison">Side-by-Side</TabsTrigger>
          <TabsTrigger value="trends">Trend Analysis</TabsTrigger>
          <TabsTrigger value="forecasts">Forecasting</TabsTrigger>
          <TabsTrigger value="rankings">State Rankings</TabsTrigger>
          <TabsTrigger value="intelligence">AI Insights</TabsTrigger>
        </TabsList>
        
        {/* Side-by-Side Comparison */}
        <TabsContent value="comparison">
          <div className="grid grid-cols-3 gap-4">
            {selectedStates.map(state => (
              <StateMetricsCard 
                key={state}
                state={state}
                timeRange={timeRange}
                showComparison={true}
              />
            ))}
          </div>
          
          {/* Statistical Comparison */}
          <Card className="mt-4">
            <CardHeader>
              <CardTitle>Statistical Significance Tests</CardTitle>
            </CardHeader>
            <CardContent>
              <StatisticalComparisonMatrix states={selectedStates} />
            </CardContent>
          </Card>
        </TabsContent>
        
        {/* Trend Overlay Chart */}
        <TabsContent value="trends">
          <Card>
            <CardHeader>
              <CardTitle>Multi-State Trend Comparison</CardTitle>
            </CardHeader>
            <CardContent>
              <LineChart data={multiStateTrends} height={400}>
                {selectedStates.map((state, index) => (
                  <Line 
                    key={state}
                    dataKey={state}
                    stroke={COLORS[index]}
                    strokeWidth={2}
                  />
                ))}
              </LineChart>
            </CardContent>
          </Card>
        </TabsContent>
        
        {/* Forecasting Comparison */}
        <TabsContent value="forecasts">
          <div className="grid grid-cols-2 gap-4">
            {selectedStates.map(state => (
              <ForecastVisualization
                key={state}
                state={state}
                model="ensemble"
                weeksAhead={4}
              />
            ))}
          </div>
          
          {/* Forecast Confidence Comparison */}
          <Card className="mt-4">
            <CardHeader>
              <CardTitle>Model Confidence Comparison</CardTitle>
            </CardHeader>
            <CardContent>
              <BarChart data={forecastConfidence}>
                <Bar dataKey="confidence" fill="#10b981" />
              </BarChart>
            </CardContent>
          </Card>
        </TabsContent>
        
        {/* Rankings Dashboard */}
        <TabsContent value="rankings">
          <StateRankingsTable 
            rankingCriteria="composite"
            timeRange={timeRange}
          />
        </TabsContent>
        
        {/* AI-Generated Insights */}
        <TabsContent value="intelligence">
          <Card>
            <CardHeader>
              <CardTitle>🤖 AI-Generated Intelligence Brief</CardTitle>
              <CardDescription>
                Automated analysis using GPT-4
              </CardDescription>
            </CardHeader>
            <CardContent>
              <AIIntelligenceBrief states={selectedStates} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

---

## Implementation Roadmap

### Phase 1: Enhanced Backend Analytics (Week 1-2)
- [ ] Create `StateComparativeAnalyzer` service
- [ ] Implement statistical comparison methods (Mann-Whitney U, Kruskal-Wallis)
- [ ] Add state clustering algorithm
- [ ] Build composite ranking system
- [ ] Create new API endpoints

### Phase 2: Advanced Forecasting (Week 3-4)
- [ ] Implement LSTM forecaster
- [ ] Implement BSTS forecaster
- [ ] Enhance ensemble meta-model with auto-calibration
- [ ] Add backtesting framework
- [ ] Implement forecast confidence scoring

### Phase 3: LLM Integration (Week 5)
- [ ] Set up OpenAI API integration
- [ ] Build intelligence report generator
- [ ] Create anomaly explanation system
- [ ] Add comparative summaries

### Phase 4: Frontend Upgrades (Week 6-7)
- [ ] Build `StateComparativeAnalytics` component
- [ ] Create forecast visualization widgets
- [ ] Add state rankings table
- [ ] Implement AI insights panel
- [ ] Add export functionality (PDF reports)

### Phase 5: Testing & Optimization (Week 8)
- [ ] Backtest forecasting models
- [ ] A/B test LLM prompt engineering
- [ ] Performance optimization
- [ ] User acceptance testing

---

## Success Metrics

### Accuracy
- Forecast MAPE < 15% for ensemble model
- Statistical tests have 95% confidence intervals
- LLM summaries 90%+ factual accuracy (human validation)

### Performance
- API response time < 1 second for comparisons
- Frontend load time < 2 seconds
- Cache hit rate > 80% for forecasts

### User Engagement
- 70% of analysts use comparative features weekly
- Average session time > 5 minutes on analytics tab
- 50% use PDF export functionality

---

## Technologies & Dependencies

### Backend
- **Statistics:** `scipy`, `statsmodels`
- **ML:** `prophet`, `pmdarima`, `tensorflow`, `pybsts`
- **LLM:** `openai` (GPT-4)
- **Caching:** Redis for forecast caching

### Frontend
- **Charts:** `recharts`, `d3.js`
- **UI:** `shadcn/ui`, `tailwindcss`
- **State Management:** React Query for API caching

---

## Cost Estimation

### LLM API Costs
- GPT-4 Turbo: ~$0.01 per report
- 1000 reports/month = $10/month
- Recommendation: Cache reports for 24 hours

### Compute
- LSTM training: ~30 minutes per state (one-time)
- BSTS inference: ~5 seconds per forecast
- Recommendation: Pre-compute daily forecasts via Celery

---

## Risk Mitigation

1. **Model Overfitting:** Use cross-validation, regularization
2. **LLM Hallucinations:** Fact-check against data, show sources
3. **Data Quality:** Add outlier detection, manual validation flags
4. **API Rate Limits:** Implement caching, rate limiting

---

## Conclusion

This upgrade transforms the basic "Conflicts by State" component into a **world-class intelligence platform** combining:
- **Statistical rigor** (hypothesis testing, clustering)
- **Proven forecasting** (Prophet, ARIMA, LSTM, BSTS ensemble)
- **AI-enhanced reporting** (LLM-generated insights)

**Expected Impact:**
- 3x more actionable insights for policymakers
- 40% improvement in forecast accuracy vs. current implementation
- Differentiation from competitors (ACLED, CrisisWatch)

---

**Next Steps:** Review proposal → Prioritize phases → Begin Phase 1 implementation

