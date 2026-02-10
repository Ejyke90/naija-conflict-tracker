-- Generated from u503102722_conflictdb (1).sql
BEGIN;
DROP TABLE IF EXISTS failed_jobs;

CREATE TABLE IF NOT EXISTS failed_jobs (
    id BIGINT NOT NULL,
    uuid VARCHAR(255) NOT NULL,
    connection TEXT NOT NULL,
    queue TEXT NOT NULL,
    payload LONGTEXT NOT NULL,
    exception LONGTEXT NOT NULL,
    failed_at TIMESTAMP NOT NULL DEFAULT current_timestamp()
);

COMMIT;
