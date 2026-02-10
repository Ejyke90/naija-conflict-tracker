-- Generated from u503102722_conflictdb (1).sql
BEGIN;
DROP TABLE IF EXISTS regions;

CREATE TABLE IF NOT EXISTS regions (
    id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NULL DEFAULT NULL,
    updated_at TIMESTAMP NULL DEFAULT NULL
);

INSERT INTO regions (id, title, created_at, updated_at) VALUES
(1, ''North East'', ''2026-01-25 10:22:29'', ''2026-01-25 10:22:29''),
(2, ''North Central'', ''2026-01-25 10:22:29'', ''2026-01-25 10:22:29''),
(3, ''North West'', ''2026-01-25 10:22:29'', ''2026-01-25 10:22:29''),
(4, ''South East'', ''2026-01-25 10:22:29'', ''2026-01-25 10:22:29''),
(5, ''South South'', ''2026-01-25 10:22:29'', ''2026-01-25 10:22:29''),
(6, ''South West'', ''2026-01-25 10:22:29'', ''2026-01-25 10:22:29'');

COMMIT;
