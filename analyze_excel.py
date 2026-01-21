import pandas as pd
import json

# Read Excel file
file_path = "Nextier's Nigeria Violent Conflicts Database Original.xlsx"
xl = pd.ExcelFile(file_path)

print('SHEET NAMES:')
print(json.dumps(xl.sheet_names, indent=2))
print('\n' + '='*80 + '\n')

# Read first sheet
df = pd.read_excel(file_path, sheet_name=xl.sheet_names[0], nrows=5)

print(f'FIRST SHEET: {xl.sheet_names[0]}')
print(f'Total columns: {len(df.columns)}')
print(f'\nCOLUMNS:')
for i, col in enumerate(df.columns, 1):
    print(f'{i}. {col}')

print('\n' + '='*80 + '\n')
print('SAMPLE DATA (first 3 rows):')
print(df.head(3).to_string())

print('\n' + '='*80 + '\n')
print('DATA TYPES:')
print(df.dtypes.to_string())

print('\n' + '='*80 + '\n')
# Get full dataset stats
df_full = pd.read_excel(file_path, sheet_name=xl.sheet_names[0])
print(f'TOTAL ROWS: {len(df_full):,}')
print(f'TOTAL COLUMNS: {len(df_full.columns)}')

# Check for null values
print('\n' + '='*80 + '\n')
print('NULL VALUE COUNTS (Top 10):')
null_counts = df_full.isnull().sum()
print(null_counts[null_counts > 0].sort_values(ascending=False).head(10).to_string())

# Check unique values for key columns
print('\n' + '='*80 + '\n')
print('UNIQUE VALUE COUNTS:')
for col in ['State', 'LGA', 'Conflict Type', 'Actor1', 'Actor2']:
    if col in df_full.columns:
        unique_count = df_full[col].nunique()
        print(f'{col}: {unique_count:,} unique values')

# Date range
print('\n' + '='*80 + '\n')
date_cols = [col for col in df_full.columns if 'date' in col.lower() or 'year' in col.lower()]
if date_cols:
    print(f'DATE COLUMNS: {date_cols}')
    for col in date_cols:
        try:
            print(f'{col}: {df_full[col].min()} to {df_full[col].max()}')
        except:
            pass

# Sample relationships
print('\n' + '='*80 + '\n')
print('DATA RELATIONSHIP ANALYSIS:')
print(f'Average events per state: {len(df_full) / df_full["State"].nunique():.1f}' if 'State' in df_full.columns else '')
print(f'Average fatalities per event: {df_full["Fatalities"].mean():.1f}' if 'Fatalities' in df_full.columns else '')

# Check for geospatial data
print('\n' + '='*80 + '\n')
print('GEOSPATIAL COLUMNS:')
geo_cols = [col for col in df_full.columns if any(term in col.lower() for term in ['lat', 'lon', 'location', 'coordinate', 'gps'])]
print(geo_cols if geo_cols else 'No explicit geospatial columns found')
