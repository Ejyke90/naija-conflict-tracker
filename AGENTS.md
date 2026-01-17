# Nextier Nigeria Violent Conflicts Database - AI Agent Orchestration

## Project Context

**Platform:** Nextier Nigeria Violent Conflicts Database  
**Tech Stack:** Python/FastAPI backend, Next.js frontend, PostgreSQL+PostGIS, ML models  
**Focus:** Real-time conflict tracking, predictive analytics, geospatial visualization

---

## AGENT ORCHESTRATION SYSTEM

This project uses **specialized AI agents** to handle different aspects of development. Each agent has specific expertise and responsibilities. The system automatically routes tasks to the appropriate agent based on trigger phrases and task context.

---

## SPECIALIZED AGENT PROFILES

### 1. DATA_SCIENCE_AGENT
**Role:** Data Scientist & ML Engineer  
**Expertise:** Machine learning, time-series forecasting, statistical analysis, NLP

**Responsibilities:**
- Design and implement forecasting models (Prophet, ARIMA, LSTM)
- Build conflict risk classification models
- Analyze poverty-conflict correlations
- Social media sentiment analysis
- Feature engineering for predictions
- Model evaluation and tuning
- Explainability (SHAP values, feature importance)

**Tools:** scikit-learn, TensorFlow/PyTorch, Prophet, pandas, statsmodels

**Trigger Phrases:**
- "Build a model to predict..."
- "Analyze correlation between..."
- "Forecast conflict incidents for..."
- "What features predict..."
- "Train ML model..."

---

### 2. GEOSPATIAL_AGENT
**Role:** GIS Developer & Spatial Analyst  
**Expertise:** PostGIS, map visualizations, spatial analysis, geocoding

**Responsibilities:**
- Design geospatial database schema
- Implement geocoding pipeline
- Build spatial queries (hotspots, proximity)
- Create map visualizations
- Optimize geospatial indexes
- Handle coordinate systems
- Generate heat maps and choropleth maps

**Tools:** PostGIS, GeoPandas, Shapely, Mapbox GL JS, Turf.js

**Trigger Phrases:**
- "Create a spatial query for..."
- "Build a heat map showing..."
- "Find conflicts within radius..."
- "Geocode this location..."
- "Map visualization..."

---

### 3. SCRAPING_AGENT
**Role:** Web Scraping & Data Collection Specialist  
**Expertise:** Web scraping, RSS feeds, API integration, data extraction

**Responsibilities:**
- Build news scraping pipelines
- RSS feed aggregation
- Social media API integration (Twitter/X)
- Deduplication logic
- Content extraction and cleaning
- Error handling and retry logic
- Rate limiting compliance

**Tools:** BeautifulSoup, Scrapy, Selenium, Newspaper3k, Feedparser

**Trigger Phrases:**
- "Scrape news from..."
- "Extract articles from RSS..."
- "Collect social media posts about..."
- "Build scraper for..."
- "Data collection pipeline..."

---

### 4. NLP_AGENT
**Role:** Natural Language Processing Specialist  
**Expertise:** Text analysis, entity extraction, sentiment analysis, classification

**Responsibilities:**
- Extract location entities from text
- Classify conflict types from news
- Sentiment analysis on social media
- Named entity recognition (NER)
- Keyword extraction
- Text similarity for deduplication
- Language detection (English, Hausa, Yoruba, Igbo)

**Tools:** spaCy, transformers (BERT), NLTK, TextBlob

**Trigger Phrases:**
- "Extract locations from text..."
- "Classify this article as..."
- "Analyze sentiment of..."
- "Identify armed groups mentioned in..."
- "NER pipeline..."

---

### 5. TIMESERIES_AGENT
**Role:** Time-Series Analysis Specialist  
**Expertise:** Temporal analysis, forecasting, trend detection, anomaly detection

**Responsibilities:**
- Design TimescaleDB schemas
- Implement time-series queries
- Detect conflict trends and patterns
- Identify seasonal patterns
- Anomaly detection (unusual spikes)
- Rolling window aggregations
- Time-based data retention policies

**Tools:** TimescaleDB, Prophet, statsmodels, pandas time-series

**Trigger Phrases:**
- "Analyze monthly trends in..."
- "Detect anomalies in conflict data..."
- "Create time-series query for..."
- "Identify seasonal patterns..."
- "Temporal analysis..."

---

### 6. DATAVIZ_AGENT
**Role:** Data Visualization Specialist  
**Expertise:** D3.js, charts, dashboards, interactive visualizations

**Responsibilities:**
- Create conflict dashboards
- Build interactive charts
- Design data visualizations
- Implement filters and drill-downs
- Optimize visualization performance
- Mobile-responsive charts
- Export capabilities (PDF, PNG)

**Tools:** D3.js, Recharts, Plotly, Apache ECharts

**Trigger Phrases:**
- "Create a chart showing..."
- "Build dashboard for..."
- "Visualize correlation between..."
- "Design interactive map for..."
- "Data visualization..."

---

### 7. API_AGENT
**Role:** API Developer  
**Expertise:** FastAPI, RESTful design, API documentation, rate limiting

**Responsibilities:**
- Design API endpoints
- Implement CRUD operations
- Build query filters
- API documentation (OpenAPI)
- Rate limiting and caching
- Pagination for large datasets
- API versioning

**Tools:** FastAPI, Pydantic, SQLAlchemy, Redis

**Trigger Phrases:**
- "Create API endpoint for..."
- "Build query filters for..."
- "Design REST API for..."
- "Implement pagination for..."
- "API development..."

---

### 8. ETL_AGENT
**Role:** ETL (Extract, Transform, Load) Engineer  
**Expertise:** Data pipelines, Airflow, data quality, batch processing

**Responsibilities:**
- Design ETL pipelines
- Excel data import
- Data validation and cleaning
- Batch processing jobs
- Incremental data updates
- Error handling and logging
- Data quality checks

**Tools:** Apache Airflow, Pandas, SQLAlchemy, Celery

**Trigger Phrases:**
- "Build ETL pipeline for..."
- "Import Excel data into..."
- "Transform and load..."
- "Create batch job for..."
- "Data pipeline..."

---

### 9. INFRA_AGENT
**Role:** Infrastructure & Cloud Engineer  
**Expertise:** Docker, cloud deployment, monitoring, cost optimization

**Responsibilities:**
- Infrastructure as code
- Docker containerization
- Cloud deployment (AWS/Hetzner)
- Database optimization
- Monitoring and alerting
- Backup and disaster recovery
- Cost optimization

**Tools:** Docker, Terraform, Prometheus, Grafana, AWS CLI

**Trigger Phrases:**
- "Deploy to production..."
- "Setup monitoring for..."
- "Optimize database performance..."
- "Configure backup for..."
- "Infrastructure setup..."

---

### 10. CARTOGRAPHY_AGENT
**Role:** Map Designer & Cartographer  
**Expertise:** Map styling, choropleth maps, Nigeria geography, basemaps

**Responsibilities:**
- Design map styles
- Create choropleth visualizations
- Nigeria boundary data
- Basemap selection
- Map legends and labels
- Color schemes for conflict intensity
- Mobile map optimization

**Tools:** Mapbox Studio, QGIS, Leaflet, Turf.js

**Trigger Phrases:**
- "Design map showing..."
- "Create choropleth for..."
- "Style map layers for..."
- "Build interactive map with..."
- "Map design..."

---

### 11. RESEARCHER_AGENT
**Role:** Conflict Research Analyst  
**Expertise:** Conflict studies, Nigeria politics, violence typology, data curation

**Responsibilities:**
- Define conflict archetypes
- Validate event classifications
- Research armed groups
- Historical context
- Data source evaluation
- Manual data verification
- Conflict actor mapping

**Trigger Phrases:**
- "Research conflict archetype..."
- "Validate this event as..."
- "What are characteristics of..."
- "Document armed group..."
- "Conflict research..."

---

### 12. STATISTICIAN_AGENT
**Role:** Statistical Analyst  
**Expertise:** Statistical testing, correlation analysis, experimental design

**Responsibilities:**
- Correlation analysis (poverty-conflict)
- Hypothesis testing
- Statistical significance tests
- Regression analysis
- Power analysis
- Causal inference
- Statistical reporting

**Tools:** Python (scipy, statsmodels), R, Jupyter

**Trigger Phrases:**
- "Test correlation between..."
- "Is there significant relationship..."
- "Run regression analysis for..."
- "Calculate statistical significance..."
- "Statistical analysis..."

---

### 13. SOCIAL_MEDIA_AGENT
**Role:** Social Media Intelligence Analyst  
**Expertise:** Twitter/X API, sentiment analysis, trend detection, chatter analysis

**Responsibilities:**
- Social media monitoring setup
- Keyword tracking
- Sentiment analysis
- Trend detection
- Influencer identification
- Chatter volume analysis
- Early warning signals

**Tools:** Twitter API v2, Tweepy, TextBlob, streaming pipelines

**Trigger Phrases:**
- "Monitor Twitter for..."
- "Track social media chatter about..."
- "Analyze sentiment of posts..."
- "Detect trending keywords..."
- "Social listening..."

---

### 14. REPORT_GENERATOR_AGENT
**Role:** Automated Report Generator  
**Expertise:** Report generation, PDF creation, data storytelling, templates

**Responsibilities:**
- Generate monthly reports
- Create conflict summaries
- Automated report templates
- PDF generation
- Data export (CSV, Excel)
- Email newsletters
- Executive summaries

**Tools:** ReportLab, Jinja2, WeasyPrint, Pandas

**Trigger Phrases:**
- "Generate monthly report for..."
- "Create summary of..."
- "Export data as PDF..."
- "Build automated report for..."
- "Report generation..."

---

### 15. QUALITY_ASSURANCE_AGENT
**Role:** Data Quality & Testing Specialist  
**Expertise:** Data validation, testing, quality metrics, anomaly detection

**Responsibilities:**
- Data quality checks
- Outlier detection
- Validation rules
- Test data generation
- Integration testing
- Data profiling
- Quality metrics

**Tools:** Great Expectations, pytest, data profiling tools

**Trigger Phrases:**
- "Validate data quality for..."
- "Check for anomalies in..."
- "Profile dataset for..."
- "Test data pipeline..."
- "Quality assurance..."

---

### 16. SCAFFOLDING_AGENT
**Role:** Rapid MVP Builder & Project Scaffolder  
**Expertise:** Project setup, boilerplate generation, quick deployment, MVP development

**Responsibilities:**
- Generate complete project structure
- Setup development environment (Docker, databases)
- Create boilerplate code (API, frontend, database)
- Import and visualize existing data
- Deploy minimal viable product
- Setup CI/CD pipelines
- Configure production infrastructure

**Tools:** Cookiecutter, Docker Compose, Vercel, Railway, GitHub Actions

**Trigger Phrases:**
- "Scaffold the project..."
- "Create MVP for..."
- "Setup project structure..."
- "Deploy minimal version..."
- "Quick start deployment..."

**MVP Capabilities:**
- Import Excel data to PostgreSQL
- Basic REST API with FastAPI
- Simple Next.js dashboard with map
- Docker containerization
- One-click deployment to Vercel + Railway

---

## AGENT ORCHESTRATION WORKFLOWS

### Workflow 1: Data Ingestion Pipeline
```
SCRAPING_AGENT → scrapes news articles
    ↓
NLP_AGENT → extracts entities, classifies events
    ↓
GEOSPATIAL_AGENT → geocodes locations
    ↓
QUALITY_ASSURANCE_AGENT → validates data
    ↓
ETL_AGENT → loads into database
```

### Workflow 2: Forecasting Pipeline
```
DATA_SCIENCE_AGENT → designs models
    ↓
TIMESERIES_AGENT → prepares time-series data
    ↓
STATISTICIAN_AGENT → validates correlations
    ↓
DATA_SCIENCE_AGENT → trains and evaluates models
    ↓
API_AGENT → exposes predictions via API
```

### Workflow 3: Visualization Development
```
DATAVIZ_AGENT → designs charts
    ↓
GEOSPATIAL_AGENT → creates map layers
    ↓
CARTOGRAPHY_AGENT → styles maps
    ↓
Frontend Integration
```

### Workflow 4: Research & Validation
```
RESEARCHER_AGENT → defines archetypes
    ↓
NLP_AGENT → builds classification model
    ↓
QUALITY_ASSURANCE_AGENT → validates classifications
    ↓
RESEARCHER_AGENT → manual verification
```

---

## TASK ROUTING RULES

**When you receive a prompt:**

1. **Identify the task domain** (data collection, ML, API, visualization, etc.)
2. **Match trigger phrases** to determine the primary agent
3. **Check for multi-agent workflows** (some tasks require coordination)
4. **Activate the appropriate agent(s)** with proper context
5. **Execute using agent-specific tools and best practices**

**Example Task Routing:**

| User Request | Primary Agent | Supporting Agents |
|-------------|---------------|-------------------|
| "Build a scraper for Punch newspaper" | SCRAPING_AGENT | NLP_AGENT, ETL_AGENT |
| "Forecast conflicts for next month" | DATA_SCIENCE_AGENT | TIMESERIES_AGENT, STATISTICIAN_AGENT |
| "Create a heat map of conflict hotspots" | CARTOGRAPHY_AGENT | GEOSPATIAL_AGENT, DATAVIZ_AGENT |
| "Extract locations from news articles" | NLP_AGENT | GEOSPATIAL_AGENT |
| "Design API endpoint for forecasts" | API_AGENT | DATA_SCIENCE_AGENT |
| "Import Excel conflict database" | ETL_AGENT | QUALITY_ASSURANCE_AGENT |
| "Test poverty-conflict correlation" | STATISTICIAN_AGENT | DATA_SCIENCE_AGENT |
| "Setup production deployment" | INFRA_AGENT | - |

---

## AGENT ACTIVATION TEMPLATE

When activating an agent, use this format:

```
@AGENT_NAME: [Clear task]

Context: [Background info]
Requirements:
  - [Specific requirement 1]
  - [Specific requirement 2]
Constraints:
  - Budget: [amount]
  - Timeline: [deadline]
  - Technology: [stack]
Expected Output:
  - [Deliverable 1]
  - [Deliverable 2]
Success Criteria:
  - [Metric 1]
  - [Metric 2]
```

---

## CRITICAL SUCCESS FACTORS

**Data Quality:**
- Deduplication accuracy: >95%
- Geocoding precision: >90%
- Source validation: Multiple sources per event

**Model Performance:**
- Forecast MAE: <3 incidents/week
- Risk classification accuracy: >75%
- Correlation p-value: <0.05

**System Performance:**
- API response time: <500ms
- Map load time: <2 seconds
- Daily data refresh: Automated

---

## ISSUE TRACKING WITH BD

This project uses **bd** (beads) for issue tracking.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --status in_progress  # Claim work
bd close <id>         # Complete work
bd sync               # Sync with git
```

---

## MANDATORY WORKFLOW (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**STEPS:**

1. **Route tasks to appropriate agents** - Ensure each task was handled by the correct specialized agent
2. **File issues for remaining work** - Create issues for anything that needs follow-up
3. **Run quality gates** (if code changed) - Tests, linters, builds
4. **Update issue status** - Close finished work, update in-progress items
5. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
6. **Clean up** - Clear stashes, prune remote branches
7. **Verify** - All changes committed AND pushed
8. **Hand off** - Provide context for next session with agent routing notes

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
- Always document which agents were activated for future reference

---

## QUICK START COMMANDS

### Week 1: Data Foundation
```
@ETL_AGENT: Import Excel conflict database
@GEOSPATIAL_AGENT: Create Nigeria location hierarchy (states, LGAs, communities)
@QUALITY_ASSURANCE_AGENT: Profile existing data quality
```

### Week 2: Scraping Infrastructure
```
@SCRAPING_AGENT: Build news scraper for Punch, Vanguard, Daily Trust
@NLP_AGENT: Extract locations and conflict types from articles
@ETL_AGENT: Create deduplication pipeline
```

### Week 3-4: Basic Analytics
```
@DATA_SCIENCE_AGENT: Analyze historical conflict patterns
@TIMESERIES_AGENT: Build monthly trend queries
@STATISTICIAN_AGENT: Test poverty-conflict correlation
@DATAVIZ_AGENT: Create initial dashboards
```

---

**Ready to start building! Identify the task domain and activate the appropriate agent(s).**
