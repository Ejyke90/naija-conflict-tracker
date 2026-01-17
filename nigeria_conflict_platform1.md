# Nigeria Conflict Reporting & Forecasting Platform
## Complete Implementation Plan - Principal Software Engineer Approach

---

## EXECUTIVE SUMMARY

**Platform Name:** ConflictWatch Nigeria (or "NaijaConflict Tracker" or "SafeZones Nigeria")

**Mission:** Build a data-driven platform to track, analyze, and forecast conflict/violence in Nigeria at state, LGA, and community levels, enabling citizens, policymakers, and researchers to make informed decisions.

**Core Value Proposition:**
- Real-time conflict tracking with geospatial visualization
- Predictive analytics for early warning
- Gender-disaggregated data
- Poverty-conflict correlation analysis
- Social media chatter analysis

---

## TABLE OF CONTENTS
1. [Platform Analysis](#platform-analysis)
2. [High-Level System Design](#high-level-system-design)
3. [Technical Architecture](#technical-architecture)
4. [Data Pipeline Architecture](#data-pipeline-architecture)
5. [Machine Learning & Forecasting](#machine-learning--forecasting)
6. [Implementation Roadmap](#implementation-roadmap)
7. [AI Agents Orchestration](#ai-agents-orchestration)
8. [Infrastructure & Costs](#infrastructure--costs)

---

## PLATFORM ANALYSIS

### Competitive Analysis Summary

#### ACLED (Armed Conflict Location & Event Data)
**Strengths:**
- Global coverage with detailed event coding
- 25+ data variables per event
- Monthly forecasting (CAST system)
- API access for researchers
- Rigorous methodology

**What We'll Adopt:**
- Event taxonomy/categorization
- Geolocation precision (village/community level)
- Time-series analysis
- Conflict actor tracking

#### ConflictForecast.org
**Strengths:**
- Beautiful heat map visualization
- 12-month risk forecasts
- Simple, digestible UI
- Country-level risk scores

**What We'll Adopt:**
- Heat map design pattern
- Risk gradient (low → high)
- Forecast confidence intervals
- Mobile-first interface

#### CrisisWatch (International Crisis Group)
**Strengths:**
- Monthly trend analysis
- "Conflict Risk Alerts" system
- Resolution opportunities tracking
- Expert commentary integration

**What We'll Adopt:**
- Alert classification system
- Deterioration/improvement tracking
- Qualitative analysis integration
- Monthly digest format

---

## HIGH-LEVEL SYSTEM DESIGN

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                         │
├────────────────────┬────────────────────┬───────────────────────┤
│  Public Web Portal │ Research Dashboard │  Mobile App (Future)  │
│  • Interactive Map │ • Data Export      │  • Alerts             │
│  • Heatmaps        │ • API Access       │  • Local Reports      │
│  • Forecasts       │ • Custom Queries   │  • Push Notifications │
│  • Reports         │ • Visualizations   │                       │
└────────────────────┴────────────────────┴───────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  • Rate Limiting   • Caching (Redis)   • Authentication         │
│  • Request Routing • API Versioning                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   APPLICATION SERVICES LAYER                     │
├─────────────────┬────────────────────┬─────────────────────────┤
│ Conflict Tracker│ Forecasting Engine │ Analysis Service        │
│ • Event CRUD    │ • ML Models        │ • Correlation Analysis  │
│ • Geospatial    │ • Risk Scores      │ • Trend Detection       │
│ • Timeline      │ • Early Warning    │ • Pattern Recognition   │
├─────────────────┼────────────────────┼─────────────────────────┤
│ Data Ingestion  │ Scraping Service   │ Social Listening        │
│ • Excel Import  │ • RSS Feeds        │ • Twitter/X API         │
│ • Manual Entry  │ • News Sites       │ • Keyword Tracking      │
│ • API Imports   │ • Deduplication    │ • Sentiment Analysis    │
└─────────────────┴────────────────────┴─────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                │
├──────────────────────┬──────────────────┬──────────────────────┤
│ PostgreSQL + PostGIS │ TimescaleDB      │ ElasticSearch        │
│ • Events             │ • Time-series    │ • Full-text search   │
│ • Locations          │ • Metrics        │ • News articles      │
│ • Actors/Groups      │ • Forecasts      │ • Social media       │
├──────────────────────┼──────────────────┼──────────────────────┤
│ Redis               │ S3/MinIO         │ MongoDB (Optional)    │
│ • Cache             │ • Media files    │ • Scraped data       │
│ • Session           │ • Reports/PDFs   │ • Raw JSON           │
└──────────────────────┴──────────────────┴──────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  EXTERNAL DATA SOURCES                           │
├─────────────────────────────────────────────────────────────────┤
│ Nigeria Bureau of Stats │ News APIs │ Twitter/X  │ NGO Reports │
│ Your Excel Database     │ RSS Feeds │ Facebook   │ ACLED API   │
└─────────────────────────────────────────────────────────────────┘
```

---

## TECHNICAL ARCHITECTURE

### Technology Stack

#### Frontend
```javascript
// Modern, Fast, Open Source
- Framework: Next.js 14 (React)
- Maps: Mapbox GL JS or Leaflet.js (open source)
- Charts: D3.js + Recharts
- UI: Tailwind CSS + shadcn/ui
- State: React Query + Zustand
- Animation: Framer Motion
```

**Why:**
- Next.js: SEO-friendly, fast, serverless-ready
- Mapbox/Leaflet: Best geospatial visualization tools
- D3.js: Powerful for custom conflict visualizations
- Free/cheap hosting on Vercel

#### Backend
```python
# Python for ML/Data Science Pipeline
- Framework: FastAPI (async, fast)
- ML/Analytics: scikit-learn, pandas, numpy
- Geospatial: GeoPandas, Shapely
- NLP: spaCy, transformers
- Task Queue: Celery + Redis
```

**Why:**
- Python dominates data science/ML
- FastAPI: Modern, auto-docs, async
- Rich ML ecosystem
- Easy integration with Jupyter for research

#### Databases
```sql
-- Primary: PostgreSQL 15+ with PostGIS
CREATE EXTENSION postgis;

-- Time-series: TimescaleDB (PostgreSQL extension)
-- For efficient storage of temporal conflict data

-- Search: ElasticSearch (or Meilisearch for cheaper alternative)
-- For fast full-text search across news/reports

-- Cache: Redis
-- For API caching, session management
```

#### Infrastructure
```yaml
# Cost-Effective Open Source Stack

Development:
  - Docker + Docker Compose
  - Local Kubernetes (minikube)
  
Production (Option A - Budget):
  - Hetzner VPS (€20/month for 8GB RAM)
  - Cloudflare (Free CDN + DNS)
  - Backblaze B2 (Storage)
  
Production (Option B - Scale):
  - AWS: EC2, RDS, S3, Lambda
  - Or: DigitalOcean managed services
```

---

## DATA PIPELINE ARCHITECTURE

### Data Collection & Ingestion

```python
# Multi-Source Data Pipeline

┌─────────────────────────────────────────────────┐
│           DATA COLLECTION LAYER                 │
├─────────────────────────────────────────────────┤
│                                                  │
│  1. NEWS SCRAPING                               │
│     ├─ RSS Feeds (Punch, Vanguard, Daily Trust) │
│     ├─ Google News API                          │
│     ├─ NewsAPI.org                              │
│     └─ Custom scrapers (Beautiful Soup)         │
│                                                  │
│  2. SOCIAL MEDIA MONITORING                     │
│     ├─ Twitter/X API (keywords)                 │
│     ├─ Facebook Graph API (limited)             │
│     └─ Keyword tracking: "attack", "kidnap"     │
│                                                  │
│  3. OFFICIAL SOURCES                            │
│     ├─ Nigeria Police Force reports             │
│     ├─ NEMA (Emergency Management)              │
│     ├─ State security agencies                  │
│     └─ NGO reports (Amnesty, HRW)               │
│                                                  │
│  4. YOUR DATABASE                               │
│     ├─ Excel import (primary/secondary sources) │
│     ├─ Manual data entry portal                 │
│     └─ Bulk upload via CSV                      │
│                                                  │
│  5. EXTERNAL APIs                               │
│     ├─ ACLED API (for validation)               │
│     ├─ GDELT Project (global events)            │
│     └─ UN OCHA (humanitarian data)              │
│                                                  │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│        PREPROCESSING & DEDUPLICATION            │
├─────────────────────────────────────────────────┤
│                                                  │
│  1. TEXT EXTRACTION                             │
│     • Remove HTML/formatting                    │
│     • Extract entities (NER)                    │
│     • Normalize text                            │
│                                                  │
│  2. DEDUPLICATION                               │
│     • Content hashing (MD5)                     │
│     • Fuzzy matching (Levenshtein)              │
│     • Time-location clustering                  │
│     • Title similarity (> 80% = duplicate)      │
│                                                  │
│  3. GEOCODING                                   │
│     • Extract location mentions                 │
│     • Match to Nigeria gazetteer                │
│     • Assign lat/long coordinates               │
│     • Validate with Google Maps API             │
│                                                  │
│  4. EVENT CLASSIFICATION                        │
│     • ML model predicts conflict type           │
│     • Extract casualty numbers                  │
│     • Identify armed groups                     │
│     • Flag gender-related data                  │
│                                                  │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│              DATA VALIDATION                    │
├─────────────────────────────────────────────────┤
│  • Cross-reference multiple sources             │
│  • Flag low-confidence events                   │
│  • Human review queue for edge cases            │
│  • Automated quality checks                     │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│         STORAGE IN TIMESCALEDB                  │
└─────────────────────────────────────────────────┘
```

### Database Schema Design

```sql
-- =============================================
-- CORE TABLES
-- =============================================

-- Conflicts/Events Table
CREATE TABLE conflicts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_date DATE NOT NULL,
    event_type VARCHAR(50) NOT NULL, -- kidnapping, armed_attack, bombing, etc.
    archetype VARCHAR(100), -- farmer-herder, banditry, terrorism, etc.
    
    -- Location (hierarchical)
    state VARCHAR(50) NOT NULL,
    lga VARCHAR(100),
    community VARCHAR(200),
    location_detail TEXT,
    coordinates GEOGRAPHY(POINT, 4326), -- PostGIS
    
    -- Casualties (gender-disaggregated)
    fatalities_male INT DEFAULT 0,
    fatalities_female INT DEFAULT 0,
    fatalities_unknown INT DEFAULT 0,
    injured_male INT DEFAULT 0,
    injured_female INT DEFAULT 0,
    injured_unknown INT DEFAULT 0,
    kidnapped_male INT DEFAULT 0,
    kidnapped_female INT DEFAULT 0,
    kidnapped_unknown INT DEFAULT 0,
    displaced INT DEFAULT 0,
    
    -- Actors
    perpetrator_group VARCHAR(200),
    target_group VARCHAR(200),
    
    -- Data provenance
    source_type VARCHAR(50), -- news, social_media, official, manual
    source_url TEXT,
    source_reliability INT CHECK (source_reliability BETWEEN 1 AND 5),
    confidence_score FLOAT CHECK (confidence_score BETWEEN 0 AND 1),
    
    -- Metadata
    description TEXT,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Convert to TimescaleDB hypertable for time-series optimization
SELECT create_hypertable('conflicts', 'event_date');

-- Create indexes
CREATE INDEX idx_conflicts_state ON conflicts(state);
CREATE INDEX idx_conflicts_lga ON conflicts(lga);
CREATE INDEX idx_conflicts_type ON conflicts(event_type);
CREATE INDEX idx_conflicts_date ON conflicts(event_date DESC);
CREATE INDEX idx_conflicts_location ON conflicts USING GIST(coordinates);

-- =============================================
-- SUPPORTING TABLES
-- =============================================

-- Archetypes (Violence Types)
CREATE TABLE archetypes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50), -- violence, crime, terrorism, intercommunal
    description TEXT,
    risk_weight FLOAT -- for forecasting
);

-- Conflict Actors/Groups
CREATE TABLE actors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    type VARCHAR(50), -- armed_group, military, police, militia, bandits
    ideology VARCHAR(100),
    active_since DATE,
    description TEXT
);

-- Geographic Boundaries (for mapping)
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    type VARCHAR(20), -- state, lga, community
    name VARCHAR(200) NOT NULL,
    parent_id INT REFERENCES locations(id),
    boundary GEOGRAPHY(MULTIPOLYGON, 4326),
    population INT,
    poverty_rate FLOAT,
    unemployment_rate FLOAT,
    metadata JSONB
);

-- Poverty Data (for correlation)
CREATE TABLE poverty_indicators (
    id SERIAL PRIMARY KEY,
    location_id INT REFERENCES locations(id),
    year INT NOT NULL,
    poverty_rate FLOAT,
    unemployment_rate FLOAT,
    gdp_per_capita FLOAT,
    education_index FLOAT,
    source VARCHAR(200),
    UNIQUE(location_id, year)
);

-- Social Media Chatter
CREATE TABLE social_chatter (
    id BIGSERIAL PRIMARY KEY,
    platform VARCHAR(50), -- twitter, facebook
    post_id VARCHAR(200) UNIQUE,
    content TEXT,
    author VARCHAR(200),
    location VARCHAR(200),
    coordinates GEOGRAPHY(POINT, 4326),
    sentiment FLOAT, -- -1 (negative) to 1 (positive)
    relevance_score FLOAT,
    keywords TEXT[],
    posted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('social_chatter', 'posted_at');

-- Forecasts
CREATE TABLE forecasts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    forecast_date DATE NOT NULL,
    target_date DATE NOT NULL, -- date being forecasted
    location_type VARCHAR(20), -- state, lga
    location_name VARCHAR(200),
    
    -- Predictions
    risk_score FLOAT CHECK (risk_score BETWEEN 0 AND 1),
    risk_level VARCHAR(20), -- low, medium, high, very_high
    predicted_incidents INT,
    predicted_casualties INT,
    
    -- Model metadata
    model_version VARCHAR(50),
    confidence_interval JSONB, -- {lower: 0.3, upper: 0.7}
    contributing_factors JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- News Articles (for full-text search)
CREATE TABLE news_articles (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    url TEXT UNIQUE,
    source VARCHAR(200),
    published_at TIMESTAMP,
    extracted_locations TEXT[],
    linked_conflict_id UUID REFERENCES conflicts(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================================
-- VIEWS FOR COMMON QUERIES
-- =============================================

-- Hot Zones (High conflict areas)
CREATE VIEW hot_zones AS
SELECT 
    state,
    lga,
    COUNT(*) as incident_count,
    SUM(fatalities_male + fatalities_female + fatalities_unknown) as total_fatalities,
    SUM(kidnapped_male + kidnapped_female + kidnapped_unknown) as total_kidnapped,
    AVG(confidence_score) as avg_confidence
FROM conflicts
WHERE event_date >= NOW() - INTERVAL '6 months'
GROUP BY state, lga
HAVING COUNT(*) >= 5
ORDER BY incident_count DESC;

-- Trend Analysis
CREATE VIEW monthly_trends AS
SELECT 
    DATE_TRUNC('month', event_date) as month,
    state,
    event_type,
    COUNT(*) as incidents,
    SUM(fatalities_male + fatalities_female + fatalities_unknown) as fatalities
FROM conflicts
GROUP BY month, state, event_type
ORDER BY month DESC;

-- Gender Analysis
CREATE VIEW gender_impact AS
SELECT 
    state,
    SUM(fatalities_male) as male_fatalities,
    SUM(fatalities_female) as female_fatalities,
    SUM(kidnapped_male) as male_kidnapped,
    SUM(kidnapped_female) as female_kidnapped
FROM conflicts
WHERE event_date >= NOW() - INTERVAL '1 year'
GROUP BY state;
```

---

## MACHINE LEARNING & FORECASTING

### Predictive Models

```python
# =============================================
# FORECASTING ARCHITECTURE
# =============================================

"""
Three-tier prediction system:
1. Time-series forecasting (ARIMA, Prophet)
2. Machine learning classification (Random Forest, XGBoost)
3. Deep learning (LSTM for sequence prediction)
"""

# ========== MODEL 1: Time Series Forecasting ==========

from prophet import Prophet
import pandas as pd

def forecast_conflict_incidents(state: str, lga: str = None, weeks_ahead: int = 4):
    """
    Use Facebook Prophet for time-series forecasting
    Predicts number of incidents in next N weeks
    """
    
    # Fetch historical data
    query = f"""
        SELECT 
            DATE_TRUNC('week', event_date) as ds,
            COUNT(*) as y
        FROM conflicts
        WHERE state = '{state}'
            {f"AND lga = '{lga}'" if lga else ""}
        GROUP BY ds
        ORDER BY ds
    """
    
    df = pd.read_sql(query, db_connection)
    
    # Train Prophet model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_prior_scale=0.05  # Detect trend changes
    )
    
    # Add regressors (if data available)
    # model.add_regressor('poverty_rate')
    # model.add_regressor('unemployment_rate')
    # model.add_regressor('social_media_chatter_volume')
    
    model.fit(df)
    
    # Make forecast
    future = model.make_future_dataframe(periods=weeks_ahead, freq='W')
    forecast = model.predict(future)
    
    return {
        'forecast': forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(weeks_ahead),
        'confidence': calculate_confidence(forecast)
    }


# ========== MODEL 2: Risk Classification ==========

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import numpy as np

class ConflictRiskClassifier:
    """
    Classify LGAs into risk levels: low, medium, high, critical
    Based on multiple indicators
    """
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        
    def prepare_features(self, lga_data):
        """
        Feature engineering for risk prediction
        """
        features = {
            # Historical conflict metrics (last 6 months)
            'incident_count_6m': lga_data['incidents_last_6_months'],
            'fatality_rate_6m': lga_data['fatalities_last_6_months'] / max(lga_data['population'], 1),
            'incident_trend': lga_data['incidents_last_month'] - lga_data['incidents_prev_month'],
            
            # Archetypes prevalence
            'banditry_rate': lga_data['banditry_incidents'] / max(lga_data['total_incidents'], 1),
            'terrorism_rate': lga_data['terrorism_incidents'] / max(lga_data['total_incidents'], 1),
            'farmer_herder_rate': lga_data['farmer_herder_incidents'] / max(lga_data['total_incidents'], 1),
            
            # Socioeconomic indicators
            'poverty_rate': lga_data.get('poverty_rate', 0.5),  # Use proxy if missing
            'unemployment_rate': lga_data.get('unemployment_rate', 0.3),
            'population_density': lga_data['population'] / lga_data['area_km2'],
            
            # Proximity to conflict zones (spatial autocorrelation)
            'nearby_conflicts': count_conflicts_within_radius(lga_data['coordinates'], radius_km=50),
            
            # Social media chatter
            'chatter_volume': lga_data.get('social_media_mentions_last_week', 0),
            'negative_sentiment_ratio': lga_data.get('negative_sentiment_ratio', 0.5),
            
            # Seasonal factors
            'is_dry_season': is_dry_season(lga_data['current_month']),
            'is_harvest_season': is_harvest_season(lga_data['current_month']),
            
            # Security presence
            'military_presence': lga_data.get('military_bases', 0),
            'police_stations': lga_data.get('police_stations', 0)
        }
        
        return np.array(list(features.values())).reshape(1, -1)
    
    def predict_risk(self, lga_name, state):
        """
        Predict risk level for next 2 weeks
        Returns: risk_level, probability, contributing_factors
        """
        # Fetch data
        lga_data = fetch_lga_metrics(lga_name, state)
        
        # Prepare features
        X = self.prepare_features(lga_data)
        X_scaled = self.scaler.transform(X)
        
        # Predict
        risk_proba = self.model.predict_proba(X_scaled)[0]
        risk_level = ['low', 'medium', 'high', 'critical'][np.argmax(risk_proba)]
        
        # Feature importance (explainability)
        feature_importance = dict(zip(
            self.model.feature_names_in_,
            self.model.feature_importances_
        ))
        
        top_factors = sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'risk_level': risk_level,
            'risk_score': max(risk_proba),
            'confidence': calculate_model_confidence(risk_proba),
            'contributing_factors': top_factors,
            'probability_distribution': {
                'low': risk_proba[0],
                'medium': risk_proba[1],
                'high': risk_proba[2],
                'critical': risk_proba[3]
            }
        }


# ========== MODEL 3: Deep Learning (LSTM) ==========

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

class ConflictSequencePredictor:
    """
    LSTM model for sequence-to-sequence conflict prediction
    Learns temporal patterns in conflict escalation
    """
    
    def __init__(self, sequence_length=12):  # 12 weeks of history
        self.sequence_length = sequence_length
        self.model = self.build_model()
    
    def build_model(self):
        model = Sequential([
            LSTM(64, return_sequences=True, input_shape=(self.sequence_length, 10)),
            Dropout(0.2),
            LSTM(32, return_sequences=False),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(4, activation='softmax')  # 4 risk levels
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def predict(self, historical_sequence):
        """
        Given sequence of past weeks, predict next week's risk
        """
        prediction = self.model.predict(historical_sequence)
        return prediction


# ========== CORRELATION ANALYSIS ==========

def analyze_poverty_conflict_correlation(state=None):
    """
    Statistical analysis: Is there relationship between poverty and conflict?
    """
    from scipy.stats import pearsonr, spearmanr
    
    query = """
        SELECT 
            l.name as lga,
            p.poverty_rate,
            COUNT(c.id) as conflict_count,
            SUM(c.fatalities_male + c.fatalities_female + c.fatalities_unknown) as total_fatalities
        FROM locations l
        JOIN poverty_indicators p ON l.id = p.location_id
        LEFT JOIN conflicts c ON c.lga = l.name
            AND c.event_date >= NOW() - INTERVAL '1 year'
        WHERE l.type = 'lga'
            {f"AND l.parent_id = (SELECT id FROM locations WHERE name = '{state}')" if state else ""}
        GROUP BY l.name, p.poverty_rate
        HAVING p.poverty_rate IS NOT NULL
    """
    
    df = pd.read_sql(query, db_connection)
    
    # Calculate correlations
    pearson_corr, pearson_p = pearsonr(df['poverty_rate'], df['conflict_count'])
    spearman_corr, spearman_p = spearmanr(df['poverty_rate'], df['conflict_count'])
    
    return {
        'pearson_correlation': pearson_corr,
        'pearson_p_value': pearson_p,
        'spearman_correlation': spearman_corr,
        'spearman_p_value': spearman_p,
        'relationship': 'direct' if pearson_corr > 0 else 'inverse',
        'strength': interpret_correlation_strength(abs(pearson_corr)),
        'data_points': len(df)
    }

def interpret_correlation_strength(corr):
    if corr < 0.3:
        return 'weak'
    elif corr < 0.7:
        return 'moderate'
    else:
        return 'strong'


# ========== SOCIAL MEDIA CHATTER PREDICTOR ==========

def analyze_chatter_predictive_power():
    """
    Test if social media chatter predicts violence
    Lag correlation: does chatter today predict conflict tomorrow?
    """
    
    # Fetch chatter volume and conflict incidents over time
    query = """
        WITH chatter_daily AS (
            SELECT 
                DATE(posted_at) as date,
                COUNT(*) as chatter_volume,
                AVG(sentiment) as avg_sentiment
            FROM social_chatter
            WHERE posted_at >= NOW() - INTERVAL '6 months'
            GROUP BY DATE(posted_at)
        ),
        conflicts_daily AS (
            SELECT 
                event_date as date,
                COUNT(*) as incidents
            FROM conflicts
            WHERE event_date >= NOW() - INTERVAL '6 months'
            GROUP BY event_date
        )
        SELECT 
            c.date,
            c.chatter_volume,
            c.avg_sentiment,
            COALESCE(cf.incidents, 0) as incidents,
            COALESCE(
                (SELECT COUNT(*) FROM conflicts 
                 WHERE event_date BETWEEN c.date + INTERVAL '1 day' 
                                      AND c.date + INTERVAL '7 days'),
                0
            ) as incidents_next_week
        FROM chatter_daily c
        LEFT JOIN conflicts_daily cf ON c.date = cf.date
        ORDER BY c.date
    """
    
    df = pd.read_sql(query, db_connection)
    
    # Lag correlation (chatter today vs incidents next week)
    corr, p_value = pearsonr(df['chatter_volume'], df['incidents_next_week'])
    
    return {
        'is_predictive': p_value < 0.05 and abs(corr) > 0.3,
        'correlation': corr,
        'p_value': p_value,
        'lead_time_days': 7,
        'interpretation': f"{'Strong' if abs(corr) > 0.5 else 'Moderate' if abs(corr) > 0.3 else 'Weak'} predictive signal"
    }
```

---

## IMPLEMENTATION ROADMAP

### Phase 0: Foundation (Weeks 1-2)

#### Week 1: Planning & Setup
**Day 1-2: Project Setup**
- [ ] Choose platform name
- [ ] Register domain (.ng, .com.ng)
- [ ] Create GitHub repository
- [ ] Setup project management (Linear, Notion)
- [ ] Define team roles (if team exists)

**Day 3-5: Data Audit**
- [ ] Review your Excel database structure
- [ ] Identify data quality issues
- [ ] Map data to schema
- [ ] Document all primary/secondary sources
- [ ] Create data dictionary

**Day 6-7: Technical Architecture Review**
- [ ] Finalize tech stack decisions
- [ ] Setup development environment
- [ ] Create Docker Compose for local dev
- [ ] Initialize database schema
- [ ] Setup CI/CD pipeline (GitHub Actions)

#### Week 2: Data Infrastructure
- [ ] Design and implement database schema
- [ ] Import existing Excel data
- [ ] Build data validation scripts
- [ ] Setup PostGIS for geospatial queries
- [ ] Create Nigeria location hierarchy (states, LGAs, communities)