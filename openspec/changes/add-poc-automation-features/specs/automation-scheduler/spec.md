# Automation Scheduler Specification

## ADDED Requirements

### Requirement: Self-Contained Background Scheduler
The system SHALL provide an integrated background scheduler that operates within the FastAPI application lifecycle without requiring external process management.

#### Scenario: Automated Scraping Every 15 Minutes
- **GIVEN** the application has started successfully
- **WHEN** the scheduler initializes
- **THEN** a cron job SHALL be registered to run every 15 minutes (`*/15 * * * *`)
- **AND** the job SHALL execute automated news scraping
- **AND** the job SHALL continue running until application shutdown

#### Scenario: Scheduler Survives Application Restart
- **GIVEN** the scheduler has been running with scheduled jobs
- **WHEN** the application is restarted
- **THEN** all registered jobs SHALL be recreated
- **AND** the next run time SHALL be calculated correctly
- **AND** no jobs SHALL be lost during restart

#### Scenario: Prevent Overlapping Job Execution
- **GIVEN** a scheduled job is currently executing
- **WHEN** the next scheduled time arrives
- **THEN** the scheduler SHALL wait for the current execution to complete
- **AND** SHALL NOT start a duplicate job instance
- **AND** SHALL log the skipped execution

### Requirement: Scheduler Status Monitoring
The system SHALL provide real-time visibility into scheduler operational state.

#### Scenario: Query Scheduler Health
- **GIVEN** the scheduler is running
- **WHEN** a client requests `/api/v1/scheduler/status`
- **THEN** the system SHALL return:
  - Current status (running/stopped)
  - Next scheduled run time (ISO 8601 format)
  - Last successful execution timestamp
  - Schedule configuration (cron expression)
  - Active job count
  - Application uptime

#### Scenario: Scheduler Not Running
- **GIVEN** the scheduler has been stopped or failed to start
- **WHEN** a client requests `/api/v1/scheduler/status`
- **THEN** the system SHALL return:
  - Status: "stopped"
  - Reason for stoppage (if available)
  - Last known state before stop

### Requirement: Manual Scheduler Control
The system SHALL allow manual control of the scheduler for administrative purposes.

#### Scenario: Manually Trigger Scraping Job
- **GIVEN** the scheduler is running
- **WHEN** an authorized user triggers `/api/v1/scheduler/trigger`
- **THEN** the scraping job SHALL execute immediately
- **AND** SHALL NOT interfere with scheduled executions
- **AND** SHALL return a task ID for tracking

#### Scenario: Pause Scheduler
- **GIVEN** the scheduler is running
- **WHEN** an authorized user calls `/api/v1/scheduler/pause`
- **THEN** all scheduled jobs SHALL be paused
- **AND** currently executing jobs SHALL complete
- **AND** no new jobs SHALL start until resumed

#### Scenario: Resume Scheduler
- **GIVEN** the scheduler is paused
- **WHEN** an authorized user calls `/api/v1/scheduler/resume`
- **THEN** the scheduler SHALL resume normal operation
- **AND** next run times SHALL be recalculated from current time

### Requirement: Execution Logging and Audit Trail
The system SHALL maintain a comprehensive log of all scheduled task executions.

#### Scenario: Log Successful Execution
- **GIVEN** a scheduled job executes successfully
- **WHEN** the job completes
- **THEN** the system SHALL record:
  - Execution timestamp
  - Job ID and name
  - Execution duration
  - Result summary (articles scraped, events processed)
  - Success status
- **AND** SHALL store in `/data/automation_logs.json`
- **AND** SHALL store in database for historical analysis

#### Scenario: Log Failed Execution
- **GIVEN** a scheduled job encounters an error
- **WHEN** the job fails
- **THEN** the system SHALL record:
  - Execution timestamp
  - Job ID and name
  - Error message and stack trace
  - Failure status
  - Retry attempts made
- **AND** SHALL alert system administrators if threshold exceeded

#### Scenario: Query Execution History
- **GIVEN** automation logs exist
- **WHEN** a client requests `/api/v1/automation/logs`
- **THEN** the system SHALL return:
  - Last 100 executions by default
  - Filterable by date range, status, job name
  - Sortable by timestamp descending
  - Pagination support for large result sets

### Requirement: Graceful Startup and Shutdown
The system SHALL manage scheduler lifecycle cleanly within the application.

#### Scenario: Application Startup
- **GIVEN** the FastAPI application is starting
- **WHEN** the startup event handler executes
- **THEN** the scheduler SHALL initialize
- **AND** all configured jobs SHALL be registered
- **AND** the first execution SHALL be scheduled
- **AND** startup SHALL complete successfully even if scheduler init fails

#### Scenario: Application Shutdown
- **GIVEN** the application receives a shutdown signal
- **WHEN** the shutdown event handler executes
- **THEN** the scheduler SHALL stop accepting new jobs
- **AND** currently executing jobs SHALL be allowed to complete (with timeout)
- **AND** scheduler resources SHALL be released cleanly
- **AND** final state SHALL be logged

### Requirement: Job Configuration and Management
The system SHALL support flexible job configuration without code changes.

#### Scenario: Configure Job Schedule
- **GIVEN** a job configuration exists
- **WHEN** the scheduler initializes
- **THEN** job schedule SHALL be read from environment variables
- **AND** SHALL fall back to default (15 minutes) if not configured
- **AND** SHALL validate cron expression syntax

#### Scenario: Disable Scheduler via Configuration
- **GIVEN** `APSCHEDULER_ENABLED=false` is set
- **WHEN** the application starts
- **THEN** the scheduler SHALL NOT initialize
- **AND** the application SHALL function normally without scheduled tasks
- **AND** manual triggers SHALL still work via Celery fallback

## Configuration

### Environment Variables
```bash
# Enable/disable scheduler
APSCHEDULER_ENABLED=true

# Scraping schedule (cron format)
SCRAPING_SCHEDULE="*/15 * * * *"  # Every 15 minutes

# Job timeouts
JOB_EXECUTION_TIMEOUT=1800  # 30 minutes
JOB_COALESCE=true          # Skip if job still running
JOB_MAX_INSTANCES=1        # Prevent concurrent executions

# Logging
AUTOMATION_LOG_FILE=/data/automation_logs.json
AUTOMATION_LOG_RETENTION=100  # Keep last 100 entries
```

### Database Schema
```sql
CREATE TABLE automation_executions (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(100) NOT NULL,
    job_name VARCHAR(200) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    duration_seconds FLOAT,
    status VARCHAR(20) NOT NULL,  -- success, failure, timeout
    result_data JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_automation_executions_job_id ON automation_executions(job_id);
CREATE INDEX idx_automation_executions_started_at ON automation_executions(started_at DESC);
```

## Dependencies

- `APScheduler >= 3.10.0` - Background job scheduling
- `pytz` - Timezone support for scheduler
- FastAPI lifecycle event handlers
- PostgreSQL for execution history
- File system for real-time logs
