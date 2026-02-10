-- Generated from u503102722_conflictdb (1).sql
BEGIN;
DROP TABLE IF EXISTS cache_locks;

CREATE TABLE IF NOT EXISTS cache_locks (
    key VARCHAR(255) NOT NULL,
    owner VARCHAR(255) NOT NULL,
    expiration INTEGER NOT NULL
);

COMMIT;
