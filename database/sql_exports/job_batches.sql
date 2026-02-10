-- Generated from u503102722_conflictdb (1).sql
BEGIN;
DROP TABLE IF EXISTS job_batches;

CREATE TABLE IF NOT EXISTS job_batches (
    id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    total_jobs INTEGER NOT NULL,
    pending_jobs INTEGER NOT NULL,
    failed_jobs INTEGER NOT NULL,
    failed_job_ids LONGTEXT NOT NULL,
    options TEXT DEFAULT NULL,
    cancelled_at INTEGER DEFAULT NULL,
    created_at INTEGER NOT NULL,
    finished_at INTEGER DEFAULT NULL
);

COMMIT;
