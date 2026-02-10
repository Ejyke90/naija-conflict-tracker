-- Generated from u503102722_conflictdb (1).sql
BEGIN;
DROP TABLE IF EXISTS countries;

CREATE TABLE IF NOT EXISTS countries (
    id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NULL DEFAULT NULL,
    updated_at TIMESTAMP NULL DEFAULT NULL
);

INSERT INTO countries (id, title, created_at, updated_at) VALUES
(1, ''Nigeria'', ''2026-01-25 11:22:30'', ''2026-01-25 11:22:30'');

COMMIT;
