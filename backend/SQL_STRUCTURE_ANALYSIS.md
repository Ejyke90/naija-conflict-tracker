# SQL File Structure Analysis

## File: u503102722_conflictdb (1).sql

## Overview
- **Total INSERT statements**: 54
- **Total records**: 4,297 conflict records
- **Kidnapping records**: 1,107 (25.8% of total)
- **Kidnapping victims**: 8,727 total
- **Date range**: 2020-2025 (historical data)
- **States covered**: 30 Nigerian states

## INSERT Statement Structure

### Pattern
```sql
INSERT INTO `conflicts` (`id`, `incidence_date`, `conflict_type_id`, `country_id`, `region_id`, 
                         `state_id`, `lga_id`, `community`, `civilian_death_male`, `civilian_death_female`, 
                         `civilian_death_unknown`, `security_death_male`, `security_death_female`, 
                         `security_death_unknown`, `injured_male`, `injured_female`, `injured_unknown`, 
                         `kidnapped_male`, `kidnapped_female`, `kidnapped_unknown`, `displaced_persons`, 
                         `displaced_male`, `displaced_female`, `actor_1`, `actor_2`, `actor_3`, 
                         `description`, `action`, `highway_roads_water`, `confirmation_verification`, 
                         `verification_level`, `source_url`, `source_contact_details`, 
                         `source_contact_pictures`, `source_metadata`, `data_source`, `reporter_id`, 
                         `created_at`, `updated_at`, `deleted_at`) VALUES 
(record1), (record2), ..., (recordN);
```

### Key Fields for Kidnapping Analysis
- **kidnapped_male**: Count of male kidnapping victims
- **kidnapped_female**: Count of female kidnapping victims  
- **kidnapped_unknown**: Count of unknown gender victims
- **incidence_date**: Date of incident (YYYY-MM-DD format)
- **state_id**: Nigerian state identifier (1-36)
- **lga_id**: Local Government Area identifier
- **community**: Community name (can be numeric ID or text)
- **actor_1**: Primary actor identifier
- **description**: Incident description text

## Data Quality Observations

### Issues Found
1. **ID Field**: Many records have `id` = 0 (needs auto-increment handling)
2. **Date Issues**: Some records have NULL or invalid dates
3. **Community Field**: Mix of numeric IDs and text names
4. **Unknown Gender**: 8,600 out of 8,727 victims marked as "unknown"

### Data Distribution
- **Gender Breakdown**: 
  - Male: 8 victims (0.1%)
  - Female: 119 victims (1.4%)
  - Unknown: 8,600 victims (98.5%)
- **Records with valid dates**: 54 out of 4,297
- **Geographic coverage**: 30 out of 36 states

## Parser Success Factors

### What Worked
1. **Multi-INSERT detection**: `re.findall()` captures all 54 statements
2. **Record parsing**: Parentheses counting handles complex nested values
3. **Quote handling**: Properly processes single and double quotes
4. **NULL handling**: Converts SQL NULL to Python None/0
5. **Error tolerance**: Continues processing individual record failures

### Critical Fix
**Old parser**: Used `re.search()` - only found first INSERT statement
**New parser**: Uses `re.findall()` - finds all 54 INSERT statements

## Migration Readiness

### Data Validation Required
1. **ID sequence**: Need proper auto-increment handling
2. **Date validation**: Ensure valid dates for all records
3. **State mapping**: Verify state_id mappings to Nigerian states
4. **LGA mapping**: Verify LGA identifiers
5. **Community cleanup**: Standardize community names/IDs

### Expected Impact
- **Current dashboard**: Shows "No data" (13 records)
- **After migration**: Will show meaningful statistics (1,107 kidnapping records)
- **Data increase**: 8,500% more kidnapping victims
- **Historical range**: 2020-2025 data available for analysis

## Next Steps
1. Apply new parser to production mariadb_parser.py
2. Test with full dataset
3. Execute complete migration
4. Validate dashboard functionality
