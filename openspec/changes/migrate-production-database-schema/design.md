# Database Migration Design Document

**Change ID:** migrate-production-database-schema  
**Version:** 1.0  
**Date:** 2026-02-08

## Architecture Overview

### Current Schema (Source)

```
conflict_events (PostgreSQL - Railway)
├── id (UUID PK)
├── event_date (Date)
├── event_type (String)
├── state (String) ❌ Not normalized
├── lga (String) ❌ Not normalized  
├── actor1, actor2 (String) ❌ Not normalized
├── fatalities, injuries (Integer) ❌ No breakdown
└── source, notes (Text)
```

### Target Schema (Destination)

```
MariaDB Schema (u503102722_conflictdb.sql)

Countries (1)
  └── Regions (6)
      └── States (37)
          └── LGAs (794)
              └── Conflicts (many)
                  ├── Actor1, Actor2, Actor3 (FK → actors)
                  ├── ConflictType (FK → conflict_types)
                  └── Detailed casualties (by gender/role)
```

## Schema Comparison Matrix

| Feature | Current Schema | New Schema | Migration Action |
|---------|---------------|------------|------------------|
| **Primary Key** | UUID | BIGINT AUTO_INCREMENT | Generate new IDs, maintain mapping |
| **Actors** | Text fields (actor1, actor2) | FKs to actors table | Extract actors, create lookup |
| **Location** | Flat (state, lga text) | Hierarchical (country→region→state→lga) | Map to normalized geography |
| **Casualties** | Total only | By gender + role | Split if possible, default to unknown |
| **Conflict Type** | Free text | FK to conflict_types | Map common types, create new if needed |
| **Timestamps** | created_at, updated_at | created_at, updated_at, deleted_at | Copy timestamps, null for deleted_at |
| **Source Metadata** | source (text) | source_url, source_metadata, verification_level | Parse and split |

## Detailed Table Specifications

### 1. actors Table
```sql
CREATE TABLE `actors` (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**Reference Data** (33 actors from new schema):
- Armed Robber(s), Bandits, Boko Haram, Civilian(s), Ethnic Groups, Farmer(s)
- Gunmen, Herder(s), Hoodlums, ISWAP, Informal Security Actors, IPOB/ESN
- Jama'atu Ansarul, Kidnappers, Lukarawa, Mahmuda, Maritime Pirates, Mob
- Protesters, Religious Groups, Security Forces, Cultists, Militants, etc.

### 2. conflict_types Table
```sql
CREATE TABLE `conflict_types` (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**Reference Data** (13 types from new schema):
1. Armed Robbery
2. Banditry  
3. Communal Violence
4. Cult Violence
5. Extra-judicial Killings
6. Farmer-Herder Conflict
7. Political Violence
8. General Violence/Criminality
9. Kidnapping
10. Mob Action
11. IPOB-related
12. Insurgency (Boko Haram/ISWAP)
13. Jama'atu Ansarul

### 3. regions Table
```sql
CREATE TABLE `regions` (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**Reference Data** (6 geo-political zones):
1. North-Central
2. North-East
3. North-West
4. South-East
5. South-South
6. South-West

### 4. states Table
```sql
CREATE TABLE `states` (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `region_id` bigint(20) UNSIGNED DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `states_region_id_foreign` (`region_id`),
  CONSTRAINT `states_region_id_foreign` FOREIGN KEY (`region_id`) 
    REFERENCES `regions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**Reference Data**: 37 entries (36 states + FCT)

### 5. lgas Table
```sql
CREATE TABLE `lgas` (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `state_id` bigint(20) UNSIGNED DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `lgas_state_id_foreign` (`state_id`),
  CONSTRAINT `lgas_state_id_foreign` FOREIGN KEY (`state_id`) 
    REFERENCES `states` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**Reference Data**: 794 LGAs

### 6. conflicts Table (Main Table)
```sql
CREATE TABLE `conflicts` (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
  `incidence_date` date NOT NULL,
  `conflict_type_id` bigint(20) UNSIGNED DEFAULT NULL,
  `country_id` bigint(20) UNSIGNED DEFAULT NULL,
  `region_id` bigint(20) UNSIGNED DEFAULT NULL,
  `state_id` bigint(20) UNSIGNED DEFAULT NULL,
  `lga_id` bigint(20) UNSIGNED DEFAULT NULL,
  `community` varchar(255) DEFAULT NULL,
  
  -- Civilian casualties (by gender)
  `civilian_death_male` int(11) DEFAULT NULL,
  `civilian_death_female` int(11) DEFAULT NULL,
  `civilian_death_unknown` int(11) DEFAULT NULL,
  
  -- Security forces casualties
  `security_death_male` int(11) DEFAULT NULL,
  `security_death_female` int(11) DEFAULT NULL,
  `security_death_unknown` int(11) DEFAULT NULL,
  
  -- Injured
  `injured_male` int(11) DEFAULT NULL,
  `injured_female` int(11) DEFAULT NULL,
  `injured_unknown` int(11) DEFAULT NULL,
  
  -- Kidnapped
  `kidnapped_male` int(11) DEFAULT NULL,
  `kidnapped_female` int(11) DEFAULT NULL,
  `kidnapped_unknown` int(11) DEFAULT NULL,
  
  -- Displacement
  `displaced_persons` enum('Yes','No') DEFAULT NULL,
  `displaced_male` int(11) DEFAULT NULL,
  `displaced_female` int(11) DEFAULT NULL,
  
  -- Actors (up to 3)
  `actor_1` bigint(20) UNSIGNED DEFAULT NULL,
  `actor_2` bigint(20) UNSIGNED DEFAULT NULL,
  `actor_3` bigint(20) UNSIGNED DEFAULT NULL,
  
  -- Event details
  `description` text DEFAULT NULL,
  `action` text DEFAULT NULL,
  `highway_roads_water` text DEFAULT NULL,
  
  -- Verification & sources
  `confirmation_verification` varchar(255) DEFAULT NULL,
  `verification_level` varchar(255) DEFAULT NULL,
  `source_url` text DEFAULT NULL,
  `source_contact_details` text DEFAULT NULL,
  `source_contact_pictures` varchar(255) DEFAULT NULL,
  `source_metadata` text DEFAULT NULL,
  `data_source` varchar(255) DEFAULT NULL,
  
  -- Metadata
  `reporter_id` bigint(20) UNSIGNED DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  
  PRIMARY KEY (`id`),
  KEY `conflicts_conflict_type_id_foreign` (`conflict_type_id`),
  KEY `conflicts_state_id_foreign` (`state_id`),
  KEY `conflicts_lga_id_foreign` (`lga_id`),
  KEY `conflicts_actor_1_foreign` (`actor_1`),
  KEY `conflicts_actor_2_foreign` (`actor_2`),
  KEY `conflicts_actor_3_foreign` (`actor_3`),
  KEY `conflicts_incidence_date_index` (`incidence_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## Data Migration Mapping

### Field Mappings

| Old Field (conflict_events) | New Field (conflicts) | Transformation |
|------------------------------|----------------------|----------------|
| id (UUID) | *Generate new BIGINT* | Create ID mapping table |
| event_date | incidence_date | Direct copy |
| event_type | conflict_type_id | Lookup in conflict_types, create if missing |
| state | state_id | Lookup by state name → get ID |
| lga | lga_id | Lookup by LGA name + state → get ID |
| actor1 | actor_1 | Lookup in actors, create if missing |
| actor2 | actor_2 | Lookup in actors, create if missing |
| fatalities | civilian_death_unknown | Map total (no gender breakdown) |
| injuries | injured_unknown | Map total (no gender breakdown) |
| source | source_url + source_metadata | Parse if URL, else metadata |
| description | description | Direct copy |
| created_at | created_at | Direct copy |
| updated_at | updated_at | Direct copy |

### Default Values for New Fields

- **country_id**: 1 (Nigeria - single country)
- **region_id**: Derived from state
- **civilian_death_male**: NULL
- **civilian_death_female**: NULL
- **security_death_male**: NULL (unless actor analysis suggests security involvement)
- **kidnapped_***: NULL (no data in current schema)
- **displaced_persons**: 'No' (unless description suggests displacement)
- **verification_level**: '1' (default confidence)
- **data_source**: 'Historical Migration'
- **deleted_at**: NULL

## Migration Scripts Structure

### Script 1: Create Schema
```sql
-- File: 001_create_reference_tables.sql
CREATE TABLE actors (...);
CREATE TABLE conflict_types (...);
CREATE TABLE regions (...);
CREATE TABLE states (...);
CREATE TABLE lgas (...);
CREATE TABLE conflicts (...);
```

### Script 2: Populate Reference Data
```sql
-- File: 002_populate_reference_data.sql
INSERT INTO actors VALUES (...);
INSERT INTO conflict_types VALUES (...);
INSERT INTO regions VALUES (...);
INSERT INTO states VALUES (...);
INSERT INTO lgas VALUES (...);
```

### Script 3: Migrate Historical Data
```python
# File: 003_migrate_conflicts.py
# Uses SQLAlchemy to:
# 1. Read from conflict_events
# 2. Transform data
# 3. Insert into conflicts table
# 4. Maintain ID mapping
```

### Script 4: Validation
```sql
-- File: 004_validate_migration.sql
-- Compare row counts
-- Verify casualty totals
-- Check foreign key integrity
```

## Index Strategy

### Performance Indexes
```sql
-- High-query columns
CREATE INDEX idx_conflicts_date ON conflicts(incidence_date);
CREATE INDEX idx_conflicts_state ON conflicts(state_id);
CREATE INDEX idx_conflicts_type ON conflicts(conflict_type_id);
CREATE INDEX idx_conflicts_created ON conflicts(created_at);

-- Composite indexes for common queries
CREATE INDEX idx_conflicts_state_date ON conflicts(state_id, incidence_date);
CREATE INDEX idx_conflicts_type_date ON conflicts(conflict_type_id, incidence_date);
```

## Rollback Procedure

### Rollback Script
```python
# rollback_migration.py
1. Switch application to use old conflict_events table
2. Drop new tables (actors, conflicts, etc.) if needed
3. Restore from backup if data corruption occurred
```

### Rollback Triggers
- Data loss >1%
- Application errors >10 per minute
- Query performance degradation >50%
- Foreign key constraint violations

## Testing Strategy

### Pre-Migration Tests (Staging)
1. **Schema Creation**: Create all tables without errors
2. **Reference Data**: Populate all lookup tables
3. **Sample Migration**: Migrate 100 random records
4. **Validation**: Verify data integrity
5. **Performance**: Test query speed
6. **Rollback**: Test rollback procedure

### Post-Migration Tests (Production)
1. **Data Integrity**: 
   - Row count matches
   - Total fatalities match
   - All states/LGAs have records
2. **Application Tests**:
   - Dashboard loads
   - API endpoints respond
   - Filters work correctly
3. **Performance**:
   - Query times <500ms
   - No timeout errors

## Monitoring Plan

### Metrics to Track
- **Database**:
  - Table sizes
  - Query execution time
  - Connection pool usage
  - Lock wait times
  
- **Application**:
  - Error rates
  - Response times
  - User sessions
  - Failed requests

### Alerting
- Error rate >5 per minute → Page on-call engineer
- Query time >2 seconds → Warning alert
- Connection pool exhaustion → Critical alert

## Security Considerations

1. **Backup**: Full database backup before migration
2. **Access Control**: Limit who can execute migration
3. **Audit Log**: Record all migration operations
4. **Sensitive Data**: Source URLs may contain sensitive info, handle carefully
5. **User Privacy**: reporter_id should link to anonymized user table

## Cost Implications

### Storage
- Old schema: ~5MB (conflict_events only)
- New schema: ~15MB (7 new tables)
- **Increase**: +10MB (within free tier limits)

### Compute
- Migration duration: ~8 hours CPU time
- Index creation: ~2 hours
- **Cost**: Negligible for one-time migration

---

**Review Required By:**
- Database Team: Schema design, indexes
- Backend Team: SQLAlchemy models, migration scripts
- QA Team: Test plan, validation criteria
