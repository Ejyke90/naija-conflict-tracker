"""Check all sheets in the Excel file"""
import sys
sys.path.insert(0, '/opt/homebrew/lib/python3.13/site-packages')
import pandas as pd
from pathlib import Path

excel_path = Path(__file__).parent.parent / "Nextier's Nigeria Violent Conflicts Database Original.xlsx"
xl = pd.ExcelFile(excel_path)

print("="*100)
for sheet_name in xl.sheet_names:
    print(f"\n📄 SHEET: {sheet_name}")
    print("="*100)
    df = pd.read_excel(excel_path, sheet_name=sheet_name, nrows=5)
    print(f"Rows (sample): {len(df)}, Columns: {len(df.columns)}")
    print(f"Columns: {list(df.columns)[:10]}")  # First 10 columns
    print("\nSample data:")
    print(df.head(3).to_string())
    print("\n")

# Now read the 'Home' sheet which likely has the main data
print("\n" + "="*100)
print("ANALYZING 'Home' SHEET (Main conflict data)")
print("="*100)

df_home = pd.read_excel(excel_path, sheet_name='Home')
print(f"\n📊 Total Records: {len(df_home):,}")
print(f"📊 Total Columns: {len(df_home.columns)}")
print(f"\n🗂️ ALL COLUMNS:")
for i, col in enumerate(df_home.columns, 1):
    print(f"{i:2d}. {col}")

# Show data types and null counts
print(f"\n📈 DATA PROFILE:")
for col in df_home.columns:
    dtype = df_home[col].dtype
    non_null = df_home[col].count()
    null_pct = ((len(df_home) - non_null) / len(df_home)) * 100
    unique = df_home[col].nunique()
    print(f"{col:40s} | {str(dtype):15s} | {unique:7,} unique | {null_pct:5.1f}% null")
