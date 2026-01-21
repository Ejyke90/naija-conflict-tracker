"""
Analyze Nextier's Nigeria Violent Conflicts Database
to determine optimal database architecture
"""
import sys
sys.path.insert(0, '/opt/homebrew/lib/python3.13/site-packages')

import pandas as pd
import json
from pathlib import Path

# Excel file path
excel_path = Path(__file__).parent.parent / "Nextier's Nigeria Violent Conflicts Database Original.xlsx"

print("="*80)
print("NEXTIER NIGERIA VIOLENT CONFLICTS DATABASE - STRUCTURE ANALYSIS")
print("="*80)

# Read Excel
xl = pd.ExcelFile(excel_path)

print(f"\n📊 SHEETS FOUND: {len(xl.sheet_names)}")
print(json.dumps(xl.sheet_names, indent=2))

# Analyze first sheet (main data)
df_sample = pd.read_excel(excel_path, sheet_name=xl.sheet_names[0], nrows=10)
df_full = pd.read_excel(excel_path, sheet_name=xl.sheet_names[0])

print(f"\n\n{'='*80}")
print(f"📋 SHEET: {xl.sheet_names[0]}")
print(f"{'='*80}")

print(f"\n📈 DATASET SIZE:")
print(f"   Total Rows: {len(df_full):,}")
print(f"   Total Columns: {len(df_full.columns)}")

print(f"\n📝 COLUMN SCHEMA ({len(df_full.columns)} columns):")
for i, col in enumerate(df_full.columns, 1):
    dtype = df_full[col].dtype
    non_null = df_full[col].count()
    null_pct = ((len(df_full) - non_null) / len(df_full)) * 100
    print(f"   {i:2d}. {col:30s} | {str(dtype):12s} | {non_null:6,} non-null ({null_pct:.1f}% null)")

print(f"\n\n{'='*80}")
print("🔍 DATA PROFILING")
print(f"{'='*80}")

# Key analytics columns
analytics_cols = {
    'State': 'Geographic dimension',
    'LGA': 'Local Government Area (sub-state)',
    'Conflict Type': 'Event classification',
    'Actor1': 'Primary armed group/actor',
    'Actor2': 'Secondary actor',
    'Fatalities': 'Death count',
    'Date': 'Temporal dimension'
}

print(f"\n🎯 KEY DIMENSIONS:")
for col, description in analytics_cols.items():
    if col in df_full.columns:
        unique = df_full[col].nunique()
        sample_values = df_full[col].dropna().unique()[:3].tolist()
        print(f"   {col:20s}: {unique:5,} unique | {description}")
        if len(sample_values) > 0:
            print(f"{'':25s}  Examples: {sample_values}")

# Date analysis
date_cols = [col for col in df_full.columns if 'date' in col.lower() or 'year' in col.lower()]
if date_cols:
    print(f"\n📅 TEMPORAL RANGE:")
    for col in date_cols:
        try:
            min_date = pd.to_datetime(df_full[col]).min()
            max_date = pd.to_datetime(df_full[col]).max()
            span_years = (max_date - min_date).days / 365.25
            print(f"   {col}: {min_date.date()} → {max_date.date()} ({span_years:.1f} years)")
        except:
            print(f"   {col}: Unable to parse as dates")

# Aggregation potential
print(f"\n📊 AGGREGATION POTENTIAL:")
if 'State' in df_full.columns:
    events_per_state = df_full.groupby('State').size()
    print(f"   States: {len(events_per_state)} total")
    print(f"   Events per state: {events_per_state.mean():.0f} avg, {events_per_state.min()} min, {events_per_state.max()} max")

if 'Fatalities' in df_full.columns:
    total_deaths = df_full['Fatalities'].sum()
    avg_deaths = df_full['Fatalities'].mean()
    print(f"   Total fatalities: {total_deaths:,}")
    print(f"   Average per incident: {avg_deaths:.1f}")

# Check for geospatial data
geo_cols = [col for col in df_full.columns if any(term in col.lower() for term in ['lat', 'lon', 'location', 'coordinate', 'gps', 'geography'])]
print(f"\n🗺️  GEOSPATIAL COLUMNS: {geo_cols if geo_cols else 'None found (will need geocoding)'}")

# Sample data
print(f"\n\n{'='*80}")
print("💾 SAMPLE RECORDS (first 3)")
print(f"{'='*80}\n")
print(df_sample.head(3).to_string())

print(f"\n\n{'='*80}")
print("🎯 DATABASE RECOMMENDATION")
print(f"{'='*80}\n")

# Analysis for database choice
has_relations = len(df_full.columns) > 5
has_geospatial = any('state' in col.lower() or 'location' in col.lower() or 'lga' in col.lower() for col in df_full.columns)
has_timeseries = len(date_cols) > 0
needs_aggregations = 'Fatalities' in df_full.columns or 'State' in df_full.columns
large_dataset = len(df_full) > 1000

print("📋 ANALYSIS FACTORS:")
print(f"   ✓ Structured tabular data: {has_relations}")
print(f"   ✓ Geospatial queries needed: {has_geospatial}")
print(f"   ✓ Time-series analysis: {has_timeseries}")
print(f"   ✓ Complex aggregations (SUM, AVG, COUNT): {needs_aggregations}")
print(f"   ✓ Large dataset ({len(df_full):,} rows): {large_dataset}")
print(f"   ✓ Multiple dimensions for analytics: {len([col for col in analytics_cols if col in df_full.columns])}")

print(f"\n🏆 RECOMMENDATION: **RELATIONAL DATABASE (PostgreSQL + PostGIS)**\n")

print("✅ REASONS:")
print("   1. Structured data with clear relationships (State → LGA → Events)")
print("   2. Complex analytical queries (GROUP BY state, SUM fatalities, COUNT events)")
print("   3. Geospatial capabilities needed (PostGIS for maps, proximity, hotspots)")
print("   4. Time-series queries (monthly trends, year-over-year comparisons)")
print("   5. ACID compliance for data integrity")
print("   6. Mature ecosystem with ORMs (SQLAlchemy), BI tools, analytics")
print("   7. Efficient indexing for fast queries on State, Date, Conflict Type")

print("\n❌ NoSQL NOT RECOMMENDED because:")
print("   • Need for complex JOINs (State + LGA + Armed Groups)")
print("   • SQL aggregations (SUM, AVG, GROUP BY) are core to analytics")
print("   • Geospatial queries require PostGIS (SQL extension)")
print("   • Strong consistency needed for conflict data accuracy")
print("   • Schema is well-defined and stable")

print("\n\n🗄️  RECOMMENDED SCHEMA:")
print("""
   conflicts (main table)
      ├── id (PRIMARY KEY)
      ├── event_date (DATE, indexed)
      ├── state (VARCHAR, indexed)
      ├── lga (VARCHAR)
      ├── location (GEOGRAPHY - PostGIS)
      ├── conflict_type (VARCHAR, indexed)
      ├── actor1 (VARCHAR)
      ├── actor2 (VARCHAR)
      ├── fatalities (INTEGER)
      ├── description (TEXT)
      └── created_at (TIMESTAMP)
   
   states (lookup table)
      ├── id (PRIMARY KEY)
      ├── name (VARCHAR, UNIQUE)
      └── geometry (GEOGRAPHY)
   
   lgas (lookup table)
      ├── id (PRIMARY KEY)
      ├── name (VARCHAR)
      ├── state_id (FOREIGN KEY → states)
      └── geometry (GEOGRAPHY)
""")

print("\n💡 CACHING STRATEGY:")
print("   • Redis for API response caching (conflict index, summary stats)")
print("   • Materialized views for pre-computed aggregations")
print("   • TimescaleDB extension for time-series optimizations")

print(f"\n{'='*80}\n")
