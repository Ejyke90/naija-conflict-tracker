# Database Migration Proposal: Production Schema & Data Migration

**Change ID:** migrate-production-database-schema  
**Status:** PENDING_APPROVAL  
**Created:** 2026-02-08  
**Author:** Principal FullStack Engineer  
**Type:** Database Migration

## Executive Summary

Migrate production database from current simplified schema (conflict_events, PostgreSQL/Railway) to comprehensive relational schema (from u503102722_conflictdb.sql) with full conflict tracking capabilities, detailed actor management, geographical hierarchies, and enhanced metadata tracking.

## Problem Statement

### Current State
- **Database**: PostgreSQL on Railway with basic conflict tracking
- **Schema**: Simplified `conflict_events` table with:
  - Basic event tracking (date, type, location)
  - Simple casualty counting (fatalities, injuries)
  - Limited actor information (actor1, actor2)
  - Flat location structure (state, lga only)
  - No detailed categorization (conflict types, regions)
  
### Gaps & Limitations
1. **No normalization** - Actors, states, LGAs stored as text instead of foreign keys
2. **Limited casualty breakdown** - No gender-specific or role-specific counts
3. **Missing metadata** - No source tracking, verification levels, or data provenance
4. **No hierarchy** - States/LGAs not linked to regions or countries
5. **Incomplete conflict classification** - Missing conflict_types, regions, actors tables
6. **Poor data quality tracking** - No verification status, source URLs, or confirmation details

### Impact
- Difficult to perform accurate analytics by actor, region, or conflict type
- Cannot track data sources and verify information
- Limited reporting capabilities for gender-specific casualties
- No support for multi-actor conflicts (currently limited to 2)
- Cannot establish geographical hierarchies for aggregation

## Proposed Solution

### New Schema Overview

**Core Tables:**
1. **conflicts** - Main incident table with detailed casualty breakdown and metadata
2. **actors** - Normalized actor/armed group catalog
3. **conflict_types** - Event classification taxonomy
4. **countries** - Country reference
5. **regions** - Geo-political regions (6 Nigerian regions)
6. **states** - 36 states + FCT
7. **lgas** - 774 Local Government Areas
8. **users** - Application users (already exists)

**Key Improvements:**
- **Detailed Casualties**: Separate fields for civilian/security deaths by gender
- **Multi-actor Support**: 3 actor fields per conflict
- **Verification Metadata**: Confirmation levels, source URLs, verification status
- **Geographical Hierarchy**: Country → Region → State → LGA → Community
- **Displacement Tracking**: Displaced persons by gender
- **Enhanced Source Tracking**: source_url, source_metadata, data_source fields

### Data Migration Strategy

**Phase 1: Schema Creation** (No Data Loss)
- Create new tables alongside existing schema
- Establish foreign key relationships
- Create indexes for performance

**Phase 2: Reference Data Population**
- Populate actors table (armed groups, security forces, ethnic groups)
- Populate conflict_types (Armed Clash, Banditry, Communal Violence, etc.)
- Populate geographical hierarchy (countries → regions → states → lgas)

**Phase 3: Historical Data Migration**
- Map existing conflict_events to new conflicts table
- Match states/LGAs to new normalized structure
- Extract and normalize actor information
- Preserve all historical casualty data

**Phase 4: Validation & Cutover**
- Verify data integrity (row counts, casualty totals match)
- Run parallel operations for 24-48 hours
- Cutover application to new schema
- Archive old schema (do not drop)

## Benefits

### For Data Analysis
- **Accurate Actor Tracking**: Query by specific armed groups
- **Gender-Disaggregated Data**: Analyze impact on women vs men
- **Regional Analysis**: Aggregate by geo-political zones
- **Source Verification**: Track data provenance and confidence levels

### For Application Features
- **Enhanced Dashboards**: Filter by conflict type, actor, region
- **Better Geocoding**: Leverage LGA/State hierarchy
- **Actor Profiles**: Build pages for specific armed groups
- **Data Quality Metrics**: Track verification levels

### For Future Development
- **ML Model Training**: Better features for forecasting
- **API Enhancements**: More granular filtering options
- **Reporting**: Gender-specific, actor-specific reports
- **Integration**: Easier to integrate external datasets

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| Data loss during migration | HIGH | LOW | Backup before migration, keep old schema, run parallel |
| Downtime >1 hour | MEDIUM | MEDIUM | Execute during low-traffic window, prepare rollback |
| Schema mismatch with code | HIGH | MEDIUM | Update SQLAlchemy models first, comprehensive testing |
| Performance degradation | MEDIUM | MEDIUM | Create proper indexes, optimize JOIN queries |
| Duplicate LGA names | LOW | HIGH | Use state+lga composite keys |

**Rollback Plan:**
- Keep old schema active for 7 days
- Application can switch back via environment variable
- Daily backups retained for 30 days

## Timeline & Dependencies

### Prerequisites
- [ ] Full database backup created
- [ ] Development/staging environment tested
- [ ] SQLAlchemy models updated
- [ ] Migration scripts reviewed

### Estimated Duration
- **Phase 1** (Schema Creation): 2 hours
- **Phase 2** (Reference Data): 4 hours
- **Phase 3** (Historical Migration): 8 hours
- **Phase 4** (Validation): 4 hours
- **Total**: ~18 hours (schedule over 3 days)

### Recommended Window
- **Start**: Friday 22:00 WAT (low traffic)
- **Complete**: Sunday 16:00 WAT
- **Monitoring**: Through Monday

## Success Criteria

- [ ] All historical conflict records migrated (zero data loss)
- [ ] Casualty totals match (old vs new schema)
- [ ] All states/LGAs properly linked to regions
- [ ] Application queries function correctly
- [ ] Dashboard loads within 2 seconds
- [ ] No errors in application logs for 24 hours post-migration

## Approval Required

**Stakeholders:**
- [x] Database Administrator
- [x] Backend Team Lead  
- [x] Frontend Team Lead
- [ ] Product Owner
- [ ] Project Manager

**Approval Deadline:** 2026-02-12

---

**Next Steps After Approval:**
1. Create detailed migration scripts
2. Update SQLAlchemy models
3. Test on staging database
4. Schedule production maintenance window
5. Execute migration
6. Monitor and validate
