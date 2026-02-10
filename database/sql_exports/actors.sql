-- Generated from u503102722_conflictdb (1).sql
BEGIN;
DROP TABLE IF EXISTS actors;

CREATE TABLE IF NOT EXISTS actors (
    id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NULL DEFAULT NULL,
    updated_at TIMESTAMP NULL DEFAULT NULL
);

INSERT INTO actors (id, title, created_at, updated_at) VALUES
(1, ''Armed Robber(s)'', ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(2, ''Bandits'', ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(3, ''Boko Haram'', ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(4, ''Civilian(s)'', ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(5, ''Ethnic Groups'', ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(6, ''Farmer(s)'', ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(7, ''Gunmen'', ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(8, ''Herder(s)'', ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(9, ''Hoodlumns'', ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(10, ''ISWAP'', ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(11, ''Informal Security Actors'', ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(12, ''Ipob/ESN'', ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(13, ''Jama\''atu Ansarul'', ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(14, ''Kidnappers'', ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(15, ''Lukarawa'', ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(16, ''Mahmuda'', ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(17, ''Maritime Pirates'', ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(18, ''Mob'', ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(19, ''Protesters'', ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(20, ''Religious Groups'', ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(21, ''Security Forces'', ''2026-01-25 10:22:28'', ''2026-01-25 10:22:28''),
(22, ''N/A'', NULL, NULL),
(23, ''Farmers(s)'', NULL, NULL),
(24, ''Cultists'', NULL, NULL),
(25, ''Militant(s)'', NULL, NULL),
(26, ''Hoodlums'', NULL, NULL),
(27, ''Neigbours'', NULL, NULL),
(28, ''Ritualists'', NULL, NULL),
(29, ''Assasins'', NULL, NULL),
(30, ''Husband'', NULL, NULL),
(31, ''Child'', NULL, NULL),
(32, ''Children'', NULL, NULL),
(33, ''Group'', NULL, NULL);

COMMIT;
