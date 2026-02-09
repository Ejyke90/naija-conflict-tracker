# Data Validation & Quarantine System

**Date:** February 9, 2026  
**Status:** Implementation Complete - Priority 1  
**Owner:** Data Engineer / Backend Team  

---

## Overview

This document describes the **Data Validation and Quarantine System** for the Naija Conflict Tracker. The system ensures data quality by validating all incoming conflict events before insertion into the database.

### Key Features

- ✅ **Automatic Validation** - Every incoming event is validated against quality rules
- ✅ **Quarantine System** - Failed events are quarantined for manual review (not discarded)
- ✅ **Batch Processing** - Validates multiple events efficiently
- ✅ **Admin APIs** - RESTful endpoints for quarantine management
- ✅ **Quality Metrics** - Track validation success rates and issues
- ✅ **Dashboard Integration** - Monitor data quality in real-time

---

## Architecture

```
NEWS SCRAPER/IMPORT
        ↓
   DATA VALIDATOR ← Validation Rules
        ↓
   ┌─────────────────┐
   │  Is Valid?      │
   └────────┬────────┘
            │
     ┌──────┴──────┐
     │             │
    YES            NO
     │             │
     ↓             ↓
  INSERT      QUARANTINE
     │             │
     ↓             ↓
DATABASE      MANUAL REVIEW
                  │
              ┌───┴────┐
              │         │
           APPROVE   REJECT
              │
              ↓
           INSERT
```

---

## Validation Rules

### 1. Required Fields

The following fields are **mandatory** for all conflict events:

| Field | Type | Description |
|-------|------|-------------|
| `event_date` | Date (YYYY-MM-DD) | When the conflict occurred |
| `state` | String | Nigerian state where conflict happened |
| `event_type` | String | Type of conflict (see valid types below) |
| `fatalities` | Integer | Number of deaths (≥ 0) |

**Failure Action:** Critical - Rejected immediately

### 2. Date Validation

- ✅ Event date must not be in the future
- ✅ Event date must be after January 1, 2000
- ✅ Format: `YYYY-MM-DD`

**Failure Action:** Critical - Rejected immediately

### 3. Location Validation

#### State Validation
Must be one of 36 Nigerian states:
```
Abia, Adamawa, Akwa Ibom, Anambra, Bauchi, Bayelsa,
Benue, Borno, Cross River, Delta, Ebonyi, Edo,
Ekiti, Enugu, Federal Capital Territory, Gombe, Imo,
Jigawa, Kaduna, Kano, Katsina, Kebbi, Kogi, Kwara,
Lagos, Nasarawa, Niger, Ogun, Ondo, Osun, Oyo,
Plateau, Rivers, Sokoto, Taraba, Yobe, Zamfara
```

**Failure Action:** Warning (can be corrected) or Critical if unknown state

#### Coordinate Validation (if provided)
- **Latitude:** Must be between 4°N and 14°N (Nigeria's range)
- **Longitude:** Must be between 2°E and 15°E (Nigeria's range)
- **Format:** Decimal degrees, e.g., 6.5244, 3.3792

**Failure Action:** Warning - Flagged for review

### 4. Casualty Numbers Validation

| Field | Maximum | Reason |
|-------|---------|--------|
| Fatalities | 1,000 | Single deadliest conflicts in Nigeria |
| Injuries | 2,000 | Multiple causalities per incident |
| Displaced | 100,000 | Major displacement events |

- ✅ All values must be non-negative (≥ 0)
- ✅ Values exceeding limits flagged as suspicious

**Failure Action:** Warning - Flagged for manual review

### 5. Conflict Type Validation

Valid conflict types:
```
Violence against civilians
Battles
Explosions/Remote violence
Protests
Riots
Strategic developments
Armed clash
Armed violence
Communal clash
Ethnic clash
Religious clash
Cultism
Kidnapping
Terrorism
Unknown
```

**Failure Action:** Warning - Event still insertable

### 6. Actor Type Validation (if provided)

Valid actor types:
```
State Forces
Armed Group
Armed Militia
Religious Group
Ethnic Group
Criminal Group
Unknown Actors
```

**Failure Action:** Warning - Event still insertable

### 7. Duplicate Detection

Checks recent database for similar events:
- **Same location** (state)
- **Same date** (within ±7 days)
- **Same primary actor**
- **Same casualty count**

**Failure Action:** Warning - Alert for potential duplicate

---

## API Endpoints

### Validation Endpoints

#### 1. Validate Single Event
```bash
POST /api/v1/data/validate-conflict
Content-Type: application/json

{
  "event_date": "2026-02-09",
  "state": "Kaduna",
  "event_type": "Armed clash",
  "fatalities": 15,
  "location": "Kauru LGA",
  "actor1": "Bandits",
  "actor2": "Vigilante group"
}

RESPONSE:
{
  "is_valid": false,
  "severity": "warning",
  "issues": [
    "Potential duplicate: Found 1 similar events in database"
  ],
  "issue_count": 1
}
```

#### 2. Validate Batch
```bash
POST /api/v1/data/validate-batch
Content-Type: application/json

{
  "events": [
    { ... event 1 ... },
    { ... event 2 ... }
  ]
}

RESPONSE:
{
  "results": [
    {
      "event": { ... },
      "is_valid": true,
      "severity": null,
      "issues": []
    }
  ],
  "summary": {
    "total_records": 2,
    "passed": 1,
    "failed": 1,
    "pass_rate": 50.0,
    "critical_issues": 0,
    "warning_issues": 1
  }
}
```

### Quarantine Management Endpoints

#### 3. Get Quarantine Queue
```bash
GET /api/v1/data/quarantine/queue?reviewed=false&severity=critical&limit=50

RESPONSE:
{
  "count": 3,
  "items": [
    {
      "id": 1,
      "source": "news_scraper",
      "severity": "critical",
      "reason": "validation_failure",
      "issues": ["Missing required field: event_date"],
      "issue_count": 1,
      "reviewed": false,
      "created_at": "2026-02-09T10:30:00",
      "raw_data": { ... }
    }
  ]
}
```

#### 4. Get Quarantine Statistics
```bash
GET /api/v1/data/quarantine/stats

RESPONSE:
{
  "total_quarantined": 45,
  "pending_review": 12,
  "critical_pending": 3,
  "approved": 28,
  "rejected": 5,
  "review_rate": 73.3
}
```

#### 5. Approve Quarantine Item
```bash
POST /api/v1/data/quarantine/{quarantine_id}/approve
Content-Type: application/json

{
  "reviewer_notes": "Verified manually - fatality count confirmed with news sources"
}

RESPONSE:
{
  "status": "approved",
  "id": 1
}
```

#### 6. Reject Quarantine Item
```bash
POST /api/v1/data/quarantine/{quarantine_id}/reject

{
  "reviewer_notes": "Event already in database (duplicate)"
}

RESPONSE:
{
  "status": "rejected",
  "id": 1
}
```

#### 7. Insert Approved Item
```bash
POST /api/v1/data/quarantine/{quarantine_id}/insert

RESPONSE:
{
  "status": "inserted",
  "conflict_event_id": "550e8400-e29b-41d4-a716-446655440000",
  "quarantine_id": 1
}
```

### Insertion Endpoints

#### 8. Insert with Validation
```bash
POST /api/v1/data/insert-conflict
Content-Type: application/json

{
  "event_date": "2026-02-09",
  "state": "Lagos",
  "event_type": "Riot",
  "fatalities": 5,
  "actor1": "Protesters",
  "source": "news_scraper"
}

RESPONSE (Success):
{
  "status": "inserted",
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "issues": []
}

RESPONSE (Quarantined):
{
  "status": "quarantined",
  "message": "Event failed validation and was sent to quarantine for review",
  "issues": ["Invalid state: 'Lagos' is not a recognized..."]
}
```

### Statistics & Monitoring

#### 9. Get Data Quality Report
```bash
GET /api/v1/data/quality-report?source=news_scraper&days=7

RESPONSE:
{
  "insertion_stats": {
    "period_days": 7,
    "total_inserted": 23,
    "verified": 15,
    "pending_verification": 8,
    "source": "news_scraper"
  },
  "quarantine_stats": {
    "total_quarantined": 12,
    "pending_review": 4,
    "critical_pending": 1,
    "approved": 6,
    "rejected": 2,
    "review_rate": 66.7
  },
  "source_specific_stats": {
    "source": "news_scraper",
    "period_days": 7,
    "total_quarantined": 8,
    "critical": 1,
    "warning": 7,
    "approved": 5,
    "approval_rate": 62.5
  }
}
```

---

## Integration Guide

### For News Scraper

```python
from app.services.data_validator import ConflictDataValidator
from app.services.insertion_service import ConflictEventInsertionService
from app.db.database import SessionLocal

# After extracting event from article
event_data = {
    "event_date": article_date,
    "state": extracted_state,
    "event_type": extracted_type,
    "fatalities": extracted_fatalities,
    "location": location_name,
    "actor1": primary_actor,
    ...
}

db = SessionLocal()
insertion_service = ConflictEventInsertionService(db)

# Insert with validation
success, event_id, issues = insertion_service.insert_with_validation(
    event_data=event_data,
    source="news_scraper",
    source_url=article_url,
    allow_warnings=False  # Critical errors only
)

if success:
    logger.info(f"Event inserted: {event_id}")
else:
    logger.warning(f"Event quarantined: {issues}")
```

### For Batch Imports

```python
# Import multiple events from Excel or CSV
events_from_file = load_events_from_excel(filepath)

insertion_service = ConflictEventInsertionService()

results = insertion_service.batch_insert_with_validation(
    events=events_from_file,
    source="excel_import",
    allow_warnings=True,  # Include events with warnings
    stop_on_critical=False  # Continue on non-critical errors
)

print(f"Inserted: {results['inserted']}")
print(f"Quarantined: {results['quarantined']}")
print(f"Failed: {results['failed']}")
```

---

## Manual Review Workflow

### Step-by-Step Process

1. **Monitor Quarantine Queue**
   ```bash
   curl "http://localhost:8000/api/v1/data/quarantine/queue?reviewed=false" \
     | jq '.items[] | {id, source, reason, issue_count}'
   ```

2. **Review Item Details**
   ```bash
   curl "http://localhost:8000/api/v1/data/quarantine/5"
   ```

3. **Verify Against Original Sources**
   - Check news URL for original article
   - Cross-reference with other databases
   - Verify casualty numbers
   - Confirm location and date

4. **Take Action**
   - **If valid:** Approve for insertion
     ```bash
     curl -X POST "http://localhost:8000/api/v1/data/quarantine/5/approve" \
       -H "Content-Type: application/json" \
       -d '{"reviewer_notes":"Verified with BBC report"}'
     ```
   
   - **If invalid:** Reject to prevent insertion
     ```bash
     curl -X POST "http://localhost:8000/api/v1/data/quarantine/5/reject" \
       -H "Content-Type: application/json" \
       -d '{"reviewer_notes":"Fatality count unverified"}'
     ```

5. **Insert Approved Items**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/data/quarantine/5/insert"
   ```

---

## Severity Levels

### Critical Severity
**Action:** Immediate rejection - item sent to quarantine for review

Issues:
- Missing required fields
- Invalid date (future or before 2000)
- Unknown state
- Negative casualty numbers

### Warning Severity
**Action:** Item insertable but flagged for review

Issues:
- Suspicious casualty numbers (high but possible)
- Invalid coordinates (outside Nigeria range)
- Unknown conflict type
- Potential duplicate detected
- Missing optional fields

---

## Database Schema

### ConflictEvent Table
```sql
-- Main table (data_validator references)
CREATE TABLE conflict_events (
    id UUID PRIMARY KEY,
    event_date DATE NOT NULL,
    state VARCHAR(50) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    fatalities INTEGER DEFAULT 0,
    ... (other fields)
    source TEXT,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
);
```

### DataQuarantine Table
```sql
-- Track validation failures
CREATE TABLE data_quarantine (
    id SERIAL PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    raw_data JSONB NOT NULL,
    validation_status VARCHAR(20),
    validation_issues JSONB,
    quarantine_reason VARCHAR(100),
    severity VARCHAR(20),
    reviewed BOOLEAN DEFAULT FALSE,
    resolution_status VARCHAR(20),
    created_at TIMESTAMP,
    reviewed_at TIMESTAMP,
    resolved_at TIMESTAMP
);
```

---

## Monitoring & Alerts

### Key Metrics to Track

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Validation Pass Rate | >95% | <85% |
| Quarantine Approval Rate | >80% | <70% |
| Critical Issues | Minimal | >5% of total |
| Review Response Time | <24 hours | >48 hours |

### Sample Monitoring Query

```bash
# Get daily quality report
curl "http://localhost:8000/api/v1/data/quality-report?days=1"

# Alert if critical pending > 5
if pending_critical > 5; then
  send_slack_message("High critical validation issues: $pending_critical")
fi
```

---

## Troubleshooting

### Issue: "Invalid state" error for valid state name

**Cause:** State name case sensitivity or whitespace

**Solution:** 
- Check exact spelling against valid states list
- Remove leading/trailing whitespace
- State names are case-insensitive in validation

### Issue: High false positive rate for duplicates

**Cause:** Duplicate detection too strict

**Solution:**
- Review duplicate detection window (currently 7 days)
- Adjust actor matching logic
- Require exact date match instead of ±7 days

### Issue: Legitimate events rejected for "suspicious" casualty numbers

**Cause:** MAX_FATALITIES_SINGLE_EVENT = 1,000 may be too low

**Solution:**
- Review deadliest events in Nigeria history
- Increase thresholds if justified
- Add event type-specific limits

---

## Future Improvements

### Planned Enhancements

1. **Machine Learning Duplicate Detection**
   - Use text similarity (TF-IDF) for smarter matching
   - Learn from manual review decisions

2. **Data Quality Dashboard**
   - Real-time validation metrics
   - Trends over time
   - Source-specific quality scoring

3. **Automated Quarantine Entry Resolution**
   - Auto-correct common issues (state name typos)
   - Suggest corrections to reviewers
   - Confidence-scored auto-approval

4. **External Data Enrichment**
   - Cross-reference with UN ACLED database
   - Validate with academic sources
   - Estimate quality score from source reputation

5. **Custom Validation Rules per Source**
   - Different thresholds for different sources
   - Source-specific conflict types
   - Historical accuracy weight

---

## FAQ

**Q: What happens if validation is bypassed?**  
A: Events should never bypass validation. All inserts must go through `ConflictEventInsertionService.insert_with_validation()`.

**Q: Can I directly insert into the database without validation?**  
A: Yes, but not recommended. Use the validation service to ensure data quality.

**Q: How long are quarantined items kept?**  
A: No automatic deletion. Requires manual review. Consider archiving rejected items after 90 days.

**Q: Can validation rules be customized?**  
A: Yes, edit `ConflictDataValidator` class. Make changes to:
- `NIGERIAN_STATES` - Add/remove states
- `VALID_CONFLICT_TYPES` - Add new conflict types
- `MAX_*` constants - Adjust casualty thresholds
- Validation rule methods - Add custom logic

---

## Implementation Checklist

- [x] Create validation service with quality rules
- [x] Create quarantine model and service
- [x] Create insertion service with validation integration
- [x] Create admin API endpoints
- [x] Document validation rules
- [x] Document manual review process
- [x] Test validation on sample data
- [ ] Integrate news scraper with validation
- [ ] Create dashboard for quarantine management
- [ ] Set up monitoring alerts
- [ ] Train team on manual review process
- [ ] Deploy to production with data migration

---

**Status:** Ready for integration with news scraper and dashboard  
**Next Steps:** Integrate validation into NLP pipeline, train admin team
