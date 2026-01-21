# DATABASE ARCHITECTURE RECOMMENDATION
## Nextier Nigeria Violent Conflicts Database

**Date:** January 21, 2026  
**Dataset Size:** 10,741 conflict records (2014-2021)  
**Data Complexity:** 43 columns with temporal, geospatial, and relational dimensions

---

## 📊 DATA ANALYSIS SUMMARY

### Main Dataset ("Home" Sheet)
- **Total Records:** 10,741 conflict events
- **Time Range:** 2014-2021 (8 years of data)
- **Geographic Coverage:** 38 states, 697 LGAs, 4,347 communities
- **Armed Actors:** 31 distinct primary actors, 26 secondary actors
- **Conflict Types:** 16 different crisis categories

### Key Dimensions
```
Temporal:    Date, Month, Year (1,817 unique dates)
Geographic:  State (38), LGA (697), Community (4,347)  
Actors:      Actor1 (31), Actor2 (26), Actor3 (13)
Events:      Crisis Type (16), Action (2)
Casualties:  Total Deaths, Civilian Deaths, GSA Deaths, Injured, Kidnapped, IDPs
Metadata:    Sources (58), URLs (5,381), Descriptions (6,332 unique)
```

---

## 🎯 RECOMMENDATION: **POSTGRESQL + POSTGIS + REDIS**

### ✅ WHY RELATIONAL DATABASE (PostgreSQL)?

#### 1. **Structured Multi-Dimensional Data**
Your data has clear hierarchical relationships:
```
State → LGA → Community → Conflict Event
Actor1 ↔ Actor2 ↔ Conflict Type
Date → Month → Year (time hierarchy)
```
✅ SQL perfectly handles this with:
- Foreign keys (referential integrity)
- JOINs (combine dimensions)
- Normalization (avoid data duplication)

#### 2. **Complex Analytical Queries**
Your analytics require:
```sql
-- Conflict Index calculation
SELECT state, 
       COUNT(*) as total_events,
       SUM(total_deaths) as fatalities,
       COUNT(DISTINCT lga) as geographic_diffusion,
       COUNT(DISTINCT actor_1) as armed_groups,
       AVG(total_deaths) as avg_fatalities_per_event
FROM conflicts
WHERE date >= '2023-01-01'
GROUP BY state
ORDER BY fatalities DESC;

-- Monthly trends
SELECT DATE_TRUNC('month', date) as month,
       COUNT(*) as incidents,
       SUM(total_deaths) as deaths
FROM conflicts
GROUP BY month
ORDER BY month;

-- Hotspot detection
SELECT state, lga, COUNT(*) as incidents
FROM conflicts
WHERE date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY state, lga
HAVING COUNT(*) > 5;
```
✅ SQL excels at aggregations (SUM, AVG, COUNT), GROUP BY, HAVING, window functions

❌ NoSQL (MongoDB) would require:
- Map-Reduce for aggregations (complex, slower)
- Application-level JOINs (inefficient)
- Denormalization (data duplication, sync issues)

#### 3. **Geospatial Requirements (PostGIS)**
Your platform needs:
- **Heat maps** - density of conflicts by location
- **Choropleth maps** - state-level severity coloring
- **Proximity queries** - conflicts within X km radius
- **Spatial joins** - match community → LGA → State geometries

```sql
-- PostGIS queries
-- Find conflicts within 50km of Lagos
SELECT * FROM conflicts
WHERE ST_DWithin(
    location::geography,
    ST_SetSRID(ST_MakePoint(3.3792, 6.5244), 4326)::geography,
    50000  -- meters
);

-- Count conflicts per state (spatial join)
SELECT s.name, COUNT(c.id) as incidents
FROM states s
JOIN conflicts c ON ST_Within(c.location, s.geometry)
GROUP BY s.name;
```

✅ PostGIS is industry-standard for geospatial analytics  
❌ MongoDB geospatial is limited (no complex spatial operations)

#### 4. **Time-Series Analysis (TimescaleDB Extension)**
Your dashboard shows:
- Monthly conflict trends
- Year-over-year comparisons
- Forecasting (Prophet/ARIMA)

```sql
-- TimescaleDB optimizations
CREATE EXTENSION IF NOT EXISTS timescaledb;
SELECT create_hypertable('conflicts', 'event_date');

-- Efficient time-bucket aggregations
SELECT time_bucket('1 month', event_date) as month,
       state,
       SUM(total_deaths) as fatalities
FROM conflicts
WHERE event_date >= NOW() - INTERVAL '2 years'
GROUP BY month, state
ORDER BY month;
```

✅ TimescaleDB optimizes time-series queries (10-100x faster)  
✅ Built-in functions: time_bucket, first(), last(), interpolate()

#### 5. **Data Integrity & ACID Compliance**
Conflict data requires:
- **Consistency:** No duplicate events
- **Accuracy:** Fatality counts must be exact
- **Auditability:** Track data changes
- **Transactions:** Import 10,741 records atomically

✅ PostgreSQL guarantees ACID compliance  
❌ NoSQL (MongoDB) has eventual consistency (data may be stale)

---

## 🗄️ RECOMMENDED DATABASE SCHEMA

### Core Tables

```sql
-- 1. Main conflicts table (hypertable for time-series)
CREATE TABLE conflicts (
    id SERIAL PRIMARY KEY,
    event_date DATE NOT NULL,
    month VARCHAR(20),
    year INTEGER,
    
    -- Geographic
    state_id INTEGER REFERENCES states(id),
    lga_id INTEGER REFERENCES lgas(id),
    community VARCHAR(255),
    location GEOGRAPHY(POINT, 4326),  -- PostGIS
    
    -- Actors
    actor1_id INTEGER REFERENCES actors(id),
    actor2_id INTEGER REFERENCES actors(id),
    actor3_id INTEGER REFERENCES actors(id),
    
    -- Crisis classification
    crisis_type_id INTEGER REFERENCES crisis_types(id),
    action VARCHAR(50),  -- 'attack' or 'armed clash'
    
    -- Casualties (indexed for aggregations)
    gsa_casualties INTEGER DEFAULT 0,
    civilian_casualties INTEGER DEFAULT 0,
    total_deaths INTEGER DEFAULT 0,
    injured_victims INTEGER DEFAULT 0,
    kidnap_victims INTEGER DEFAULT 0,
    idps INTEGER DEFAULT 0,
    
    -- Metadata
    description TEXT,
    confirmation_verification TEXT,
    source VARCHAR(255),
    source_url TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_event_date (event_date DESC),
    INDEX idx_state_id (state_id),
    INDEX idx_crisis_type (crisis_type_id),
    INDEX idx_total_deaths (total_deaths DESC),
    INDEX idx_location USING GIST(location)
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('conflicts', 'event_date');


-- 2. States lookup table
CREATE TABLE states (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    region VARCHAR(50),  -- North West, South East, etc.
    geometry GEOGRAPHY(MULTIPOLYGON, 4326),  -- State boundaries
    population INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);


-- 3. LGAs (Local Government Areas)
CREATE TABLE lgas (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    state_id INTEGER REFERENCES states(id),
    geometry GEOGRAPHY(MULTIPOLYGON, 4326),
    population INTEGER,
    UNIQUE(name, state_id)
);


-- 4. Actors (Armed Groups)
CREATE TABLE actors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(50),  -- Bandits, Boko Haram, Ethnic Groups, etc.
    description TEXT
);


-- 5. Crisis Types
CREATE TABLE crisis_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,  -- Terrorism, Banditry, Communal Clash, etc.
    severity_level INTEGER  -- 1=Low, 5=Extreme
);


-- 6. Pre-computed materialized views (for caching)
CREATE MATERIALIZED VIEW conflict_index_monthly AS
SELECT 
    state_id,
    DATE_TRUNC('month', event_date) as month,
    COUNT(*) as total_events,
    SUM(total_deaths) as fatalities,
    COUNT(DISTINCT lga_id) as affected_lgas,
    COUNT(DISTINCT actor1_id) as armed_groups,
    AVG(total_deaths) as avg_fatalities_per_event
FROM conflicts
GROUP BY state_id, month
WITH DATA;

-- Refresh hourly
CREATE INDEX ON conflict_index_monthly (state_id, month);
```

---

## 🚀 CACHING STRATEGY (Redis)

Use **Redis** for API response caching:

```python
# Cache conflict index for 1 hour
@cache.memoize(timeout=3600)
def get_conflict_index(time_range='12months'):
    return db.query("""
        SELECT * FROM conflict_index_monthly
        WHERE month >= NOW() - INTERVAL %s
    """, time_range)
```

**What to cache:**
- Conflict Index rankings (1 hour TTL)
- Summary statistics (30 minutes TTL)
- State-level aggregations (1 hour TTL)
- Monthly trends (1 day TTL - historical data doesn't change)

**Cache invalidation:**
- On new conflict data import
- After manual edits
- Background job refreshes materialized views every hour

---

## ⚡ PERFORMANCE OPTIMIZATIONS

### 1. Indexes
```sql
-- Critical indexes for your queries
CREATE INDEX idx_state_date ON conflicts(state_id, event_date DESC);
CREATE INDEX idx_crisis_type_date ON conflicts(crisis_type_id, event_date DESC);
CREATE INDEX idx_actor1 ON conflicts(actor1_id) WHERE actor1_id IS NOT NULL;
CREATE INDEX idx_fatalities ON conflicts(total_deaths DESC) WHERE total_deaths > 0;

-- Geospatial index
CREATE INDEX idx_location_gist ON conflicts USING GIST(location);
```

### 2. Partitioning (for scaling to 100K+ records)
```sql
-- Partition by year
CREATE TABLE conflicts_2024 PARTITION OF conflicts
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### 3. Connection Pooling
```python
# SQLAlchemy connection pool
engine = create_engine(
    'postgresql://user:pass@host/db',
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True
)
```

---

## ❌ WHY NOT NoSQL (MongoDB)?

### Issues with NoSQL for your use case:

1. **No efficient JOINs**
   - Need to denormalize (duplicate state data in every conflict)
   - Application-level joins (slow, memory-intensive)

2. **Weak aggregation**
   ```javascript
   // MongoDB aggregation pipeline (complex, verbose)
   db.conflicts.aggregate([
       {$match: {date: {$gte: ISODate("2024-01-01")}}},
       {$group: {_id: "$state", total: {$sum: 1}}},
       {$sort: {total: -1}}
   ])
   ```
   vs.
   ```sql
   -- PostgreSQL (simple, optimized)
   SELECT state, COUNT(*) 
   FROM conflicts 
   WHERE date >= '2024-01-01' 
   GROUP BY state 
   ORDER BY COUNT(*) DESC;
   ```

3. **No geospatial analytics**
   - MongoDB geospatial is basic (point queries only)
   - No spatial joins, no complex polygon operations
   - PostGIS is industry-standard

4. **Eventual consistency**
   - Conflict data needs strong consistency
   - Can't have stale fatality counts

5. **No time-series optimization**
   - MongoDB lacks TimescaleDB's time-bucket functions
   - No automatic data retention policies
   - No continuous aggregations

---

## 📦 MIGRATION PLAN

### Step 1: Create PostgreSQL Database
```bash
# Railway deployment
railway project create naija-conflict-db
railway add postgresql
railway add redis
```

### Step 2: Import Excel Data
```python
# scripts/import_excel_to_postgres.py
import pandas as pd
from sqlalchemy import create_engine

# Read Excel
df = pd.read_excel("Nextier's Nigeria Violent Conflicts Database Original.xlsx", sheet_name='Home')

# Clean data
df['Date'] = pd.to_datetime(df['Date '], errors='coerce')
df['Total Deaths'] = df['Total Deaths'].fillna(0).astype(int)

# Import to PostgreSQL
engine = create_engine('postgresql://...')
df.to_sql('conflicts_raw', engine, if_exists='replace')

# Geocode locations (use Nominatim API)
for idx, row in df.iterrows():
    location = f"{row['Communiity']}, {row['LGA']}, {row['State']}, Nigeria"
    coords = geocode(location)  # Returns (lat, lon)
    df.at[idx, 'latitude'] = coords[0]
    df.at[idx, 'longitude'] = coords[1]

# Insert into normalized schema
# ... (map to states, lgas, actors tables)
```

### Step 3: Enable Extensions
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS timescaledb;
```

### Step 4: Create Materialized Views
```sql
CREATE MATERIALIZED VIEW conflict_index_cache AS
SELECT ... (pre-compute conflict index)
WITH DATA;
```

### Step 5: Update API Endpoints
```python
# Replace mock data with real queries
@router.get("/conflict-index")
async def get_conflict_index(db: Session = Depends(get_db)):
    return db.execute("""
        SELECT state, total_events, fatalities, ...
        FROM conflict_index_cache
        ORDER BY fatalities DESC
    """).fetchall()
```

---

## 💰 COST ESTIMATE

**Railway Deployment:**
- PostgreSQL (Hobby Plan): $5/month (512MB RAM, 1GB storage)
- Redis (Hobby Plan): $5/month (256MB RAM)
- **Total: $10/month**

(Scales to Pro plan for $25/month with 8GB RAM, 100GB storage)

---

## ✅ FINAL RECOMMENDATION

**Use PostgreSQL + PostGIS + TimescaleDB + Redis**

### Justification:
1. ✅ **10,741 records** with 43 columns → Structured, relational data
2. ✅ **38 states, 697 LGAs** → Geographic hierarchy (foreign keys)
3. ✅ **Complex analytics** → SQL aggregations (SUM, AVG, COUNT, GROUP BY)
4. ✅ **Geospatial queries** → PostGIS for maps, hotspots, proximity
5. ✅ **Time-series analysis** → TimescaleDB for trends, forecasting
6. ✅ **Data integrity** → ACID compliance for accurate conflict data
7. ✅ **Performance** → Indexes, materialized views, connection pooling
8. ✅ **Caching** → Redis for API responses (sub-100ms latency)
9. ✅ **Scalability** → Partitioning, replication for growth
10. ✅ **Ecosystem** → SQLAlchemy ORM, Alembic migrations, pgAdmin, Metabase BI tools

### Migration Priority:
1. **Week 1:** Setup PostgreSQL on Railway, create schema
2. **Week 2:** Import 10,741 Excel records, geocode locations
3. **Week 3:** Create materialized views, enable TimescaleDB
4. **Week 4:** Integrate API endpoints, deploy Redis caching
5. **Week 5:** Performance tuning (indexes, query optimization)

---

**Prepared by: @ETL_AGENT, @GEOSPATIAL_AGENT, @TIMESERIES_AGENT**  
**Reviewed by: @INFRA_AGENT, @DATA_SCIENCE_AGENT**
