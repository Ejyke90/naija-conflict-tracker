-- Generated from u503102722_conflictdb (1).sql
BEGIN;
DROP TABLE IF EXISTS jobs;

CREATE TABLE IF NOT EXISTS jobs (
    id BIGINT NOT NULL,
    queue VARCHAR(255) NOT NULL,
    payload LONGTEXT NOT NULL,
    attempts SMALLINT NOT NULL,
    reserved_at INTEGER DEFAULT NULL,
    available_at INTEGER NOT NULL,
    created_at INTEGER NOT NULL
);

COMMIT;
