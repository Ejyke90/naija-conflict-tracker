-- Generated from u503102722_conflictdb (1).sql
BEGIN;
DROP TABLE IF EXISTS conflict_types;

CREATE TABLE IF NOT EXISTS conflict_types (
    id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT DEFAULT NULL,
    created_at TIMESTAMP NULL DEFAULT NULL,
    updated_at TIMESTAMP NULL DEFAULT NULL
);

INSERT INTO conflict_types (id, title, description, created_at, updated_at) VALUES
(1, ''Armed Robbery'', NULL, ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(2, ''Banditry'', NULL, ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(3, ''Communal Clash'', NULL, ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(4, ''Cult Clashes'', NULL, ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(5, ''Extra-Judicial Killings'', NULL, ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(6, ''Farmer - Herder Conflict'', NULL, ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(7, ''Group Violence'', NULL, ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(8, ''Gunmen Attacks'', NULL, ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(9, ''Kidnapping'', NULL, ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(10, ''Maritime Piracy'', NULL, ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(11, ''Secessionism'', NULL, ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(12, ''Terrorism'', NULL, ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(13, ''Militancy'', NULL, NULL, NULL),
(14, ''Civil Unrest'', NULL, NULL, NULL);

COMMIT;
