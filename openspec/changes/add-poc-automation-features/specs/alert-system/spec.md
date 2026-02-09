# Alert System Specification

## ADDED Requirements

### Requirement: High-Risk Threshold Detection
The system SHALL automatically detect and alert on conflict events that exceed configurable risk thresholds.

#### Scenario: Detect High-Risk Event
- **GIVEN** a conflict event with risk_score = 92
- **AND** alert threshold is configured as 85
- **WHEN** risk scoring completes
- **THEN** the system SHALL trigger a high-risk alert
- **AND** SHALL create alert record in database
- **AND** SHALL write alert to file webhook (`/data/high_risk_alerts.json`)
- **AND** SHALL complete within 1 second of detection

#### Scenario: Event Below Threshold
- **GIVEN** a conflict event with risk_score = 70
- **AND** alert threshold is configured as 85
- **WHEN** risk scoring completes
- **THEN** the system SHALL NOT trigger an alert
- **AND** SHALL store event normally without alerting

#### Scenario: Configurable Threshold
- **GIVEN** alert threshold can be configured
- **WHEN** `ALERT_RISK_THRESHOLD` is set to 90
- **THEN** only events with risk_score > 90 SHALL trigger alerts
- **AND** threshold change SHALL take effect immediately without restart

### Requirement: Multi-Channel Alert Delivery
The system SHALL support multiple notification channels for high-risk alerts.

#### Scenario: File-Based Webhook for UI
- **GIVEN** a high-risk alert is triggered
- **WHEN** alert is created
- **THEN** the system SHALL write alert to `/data/high_risk_alerts.json`
- **AND** SHALL maintain last 20 alerts in rolling buffer
- **AND** file SHALL be readable by frontend service
- **AND** SHALL include timestamp, event details, risk score

#### Scenario: Database Storage for History
- **GIVEN** a high-risk alert is triggered
- **WHEN** alert is created
- **THEN** the system SHALL store alert in database
- **AND** SHALL retain alerts indefinitely for analysis
- **AND** SHALL link to original conflict event
- **AND** SHALL track acknowledgment status

#### Scenario: Email Notification (Optional)
- **GIVEN** email notifications are enabled
- **AND** a high-risk alert is triggered
- **WHEN** alert threshold is exceeded
- **THEN** the system SHALL send email to configured recipients
- **AND** SHALL include event summary and link to dashboard
- **AND** SHALL retry email sending if initial attempt fails

#### Scenario: Slack/Webhook Integration (Optional)
- **GIVEN** Slack webhook URL is configured
- **AND** a high-risk alert is triggered
- **WHEN** alert is created
- **THEN** the system SHALL post notification to Slack channel
- **AND** SHALL format as rich message with event details
- **AND** SHALL continue operation if Slack API fails

### Requirement: Real-Time Alert Polling for UI
The system SHALL provide efficient polling mechanism for frontend to receive alerts with minimal latency.

#### Scenario: Frontend Polls for New Alerts
- **GIVEN** frontend is monitoring for alerts
- **WHEN** polling interval triggers (every 5 seconds)
- **THEN** the system SHALL return alerts created since last poll
- **AND** response SHALL include only new/unread alerts
- **AND** response time SHALL be <100ms

#### Scenario: Alert Read Tracking
- **GIVEN** alerts have been displayed to user
- **WHEN** user acknowledges or views alert
- **THEN** the system SHALL mark alert as read
- **AND** SHALL NOT return alert in subsequent polls
- **AND** SHALL maintain read/unread state per user

#### Scenario: Long-Polling Support
- **GIVEN** frontend requests long-polling
- **WHEN** no new alerts exist
- **THEN** the system SHALL hold connection for up to 30 seconds
- **AND** SHALL return immediately when new alert arrives
- **AND** SHALL return empty result if timeout reached

### Requirement: Alert Deduplication
The system SHALL prevent duplicate alerts for the same or similar events.

#### Scenario: Same Event Re-Scored
- **GIVEN** a conflict event has already triggered an alert
- **WHEN** the same event is re-scored (e.g., after data update)
- **THEN** the system SHALL NOT create duplicate alert
- **AND** SHALL update existing alert if risk score changed significantly
- **AND** SHALL log the update

#### Scenario: Similar Events in Short Time Window
- **GIVEN** multiple events in same location within 1 hour
- **AND** all exceed alert threshold
- **WHEN** processing multiple events
- **THEN** the system SHALL group similar alerts
- **AND** SHALL create single alert with multiple events
- **AND** SHALL prevent alert fatigue

### Requirement: Alert Prioritization and Categorization
The system SHALL categorize alerts by severity and type for efficient triage.

#### Scenario: Critical Alert (Risk > 95)
- **GIVEN** a conflict event with risk_score = 97
- **WHEN** alert is created
- **THEN** the system SHALL mark as "CRITICAL" priority
- **AND** SHALL use red color coding in UI
- **AND** SHALL trigger sound notification (if enabled)
- **AND** SHALL escalate to administrators immediately

#### Scenario: High Alert (Risk 85-95)
- **GIVEN** a conflict event with risk_score = 88
- **WHEN** alert is created
- **THEN** the system SHALL mark as "HIGH" priority
- **AND** SHALL use orange color coding in UI
- **AND** SHALL notify standard monitoring channels

#### Scenario: Alert by Conflict Type
- **GIVEN** a high-risk alert is created
- **WHEN** conflict type is known (e.g., "Kidnapping")
- **THEN** the system SHALL tag alert with conflict type
- **AND** SHALL allow filtering alerts by type
- **AND** SHALL route to specialized response teams if configured

### Requirement: Alert Acknowledgment and Resolution
The system SHALL track alert lifecycle from creation to resolution.

#### Scenario: Acknowledge Alert
- **GIVEN** an unacknowledged alert exists
- **WHEN** a user acknowledges the alert
- **THEN** the system SHALL record:
  - Acknowledgment timestamp
  - Acknowledging user
  - Optional acknowledgment notes
- **AND** SHALL change alert status to "ACKNOWLEDGED"
- **AND** SHALL notify other users of acknowledgment

#### Scenario: Resolve Alert
- **GIVEN** an alert has been addressed
- **WHEN** a user marks alert as resolved
- **THEN** the system SHALL record:
  - Resolution timestamp
  - Resolving user
  - Resolution actions taken
  - Outcome
- **AND** SHALL change alert status to "RESOLVED"
- **AND** SHALL remove from active alerts list

#### Scenario: Auto-Resolve Stale Alerts
- **GIVEN** an alert has been open for 7 days
- **AND** no activity recorded
- **WHEN** auto-resolve job runs
- **THEN** the system SHALL automatically mark as "AUTO_RESOLVED"
- **AND** SHALL add note about auto-resolution
- **AND** SHALL notify relevant users

### Requirement: Alert Analytics and Reporting
The system SHALL provide insights into alert patterns and system performance.

#### Scenario: Alert Statistics Dashboard
- **GIVEN** historical alert data exists
- **WHEN** user requests alert statistics
- **THEN** the system SHALL return:
  - Total alerts by time period
  - Alerts by priority level
  - Alerts by conflict type
  - Average acknowledgment time
  - Average resolution time
  - Alert trends over time

#### Scenario: Alert Response Metrics
- **GIVEN** resolved alerts with timestamps
- **WHEN** calculating response metrics
- **THEN** the system SHALL compute:
  - Mean time to acknowledgment
  - Mean time to resolution
  - Percentage of alerts auto-resolved
  - User response rates

## Configuration

### Environment Variables
```bash
# Alert Thresholds
ALERT_RISK_THRESHOLD=85
ALERT_CRITICAL_THRESHOLD=95

# File-Based Webhooks
ALERT_FILE_PATH=/data/high_risk_alerts.json
ALERT_FILE_MAX_SIZE=20  # Keep last 20 alerts

# Notification Channels
ALERT_EMAIL_ENABLED=false
ALERT_EMAIL_RECIPIENTS=admin@example.com,ops@example.com
ALERT_SLACK_ENABLED=false
ALERT_SLACK_WEBHOOK_URL=https://hooks.slack.com/...

# Deduplication
ALERT_DEDUP_TIME_WINDOW=3600  # 1 hour in seconds
ALERT_DEDUP_DISTANCE_THRESHOLD=10  # km

# Auto-Resolution
ALERT_AUTO_RESOLVE_DAYS=7

# UI Polling
ALERT_POLL_INTERVAL=5  # seconds
ALERT_LONG_POLL_TIMEOUT=30  # seconds
```

### Database Schema
```sql
CREATE TABLE alert_events (
    id SERIAL PRIMARY KEY,
    conflict_event_id INTEGER REFERENCES conflict_events_new(id),
    alert_type VARCHAR(20) NOT NULL,  -- HIGH, CRITICAL
    risk_score FLOAT NOT NULL,
    priority INTEGER NOT NULL,  -- 1=CRITICAL, 2=HIGH
    status VARCHAR(20) DEFAULT 'ACTIVE',  -- ACTIVE, ACKNOWLEDGED, RESOLVED, AUTO_RESOLVED
    location_state VARCHAR(100),
    location_lga VARCHAR(100),
    conflict_category VARCHAR(100),
    title TEXT NOT NULL,
    summary TEXT,
    
    -- Acknowledgment tracking
    acknowledged_at TIMESTAMP,
    acknowledged_by_user_id INTEGER REFERENCES users(id),
    acknowledgment_notes TEXT,
    
    -- Resolution tracking
    resolved_at TIMESTAMP,
    resolved_by_user_id INTEGER REFERENCES users(id),
    resolution_notes TEXT,
    resolution_actions JSONB,
    
    -- Notification tracking
    notified_channels JSONB,  -- {email: true, slack: true, webhook: true}
    notification_sent_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_alert_events_status ON alert_events(status);
CREATE INDEX idx_alert_events_created_at ON alert_events(created_at DESC);
CREATE INDEX idx_alert_events_risk_score ON alert_events(risk_score DESC);
CREATE INDEX idx_alert_events_conflict_event ON alert_events(conflict_event_id);

-- Alert read tracking (per user)
CREATE TABLE alert_read_status (
    id SERIAL PRIMARY KEY,
    alert_id INTEGER REFERENCES alert_events(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    read_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(alert_id, user_id)
);
```

### Alert File Format (JSON)
```json
{
  "alerts": [
    {
      "id": 1234,
      "timestamp": "2026-02-08T15:30:00Z",
      "alert_type": "HIGH",
      "risk_score": 92,
      "event_id": 5678,
      "title": "Armed bandits attack village in Zamfara",
      "location": {
        "state": "Zamfara",
        "lga": "Anka",
        "coordinates": [6.96, 12.11]
      },
      "conflict_type": "Banditry",
      "casualties": {
        "deaths": 15,
        "injuries": 23
      },
      "summary": "Armed bandits attacked Gidan Goga village...",
      "source": "Premium Times"
    }
  ],
  "last_updated": "2026-02-08T15:30:02Z",
  "total_count": 1
}
```

## Dependencies

- File system access for webhook files
- PostgreSQL for alert storage
- Optional: SMTP server for email notifications
- Optional: Slack API for chat notifications
- Frontend polling mechanism (5-second interval)
