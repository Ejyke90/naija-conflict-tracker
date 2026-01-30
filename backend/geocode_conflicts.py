import sys
import pandas as pd
from app.models.conflict import ConflictEvent
from app.db.database import SessionLocal

# Load LGA coordinates
lga_data = pd.read_csv('./data/nigeria_lgas.csv')
print(f"Loaded {len(lga_data)} LGAs from CSV")

# Create a lookup dictionary
lga_coords = {}
for _, row in lga_data.iterrows():
    key = (row['state'].strip(), row['lga'].strip())
    lga_coords[key] = (float(row['latitude']), float(row['longitude']))

print(f"Created lookup with {len(lga_coords)} unique state-LGA combinations")

# Connect to database
db = SessionLocal()

# Get all conflicts without coordinates
conflicts = db.query(ConflictEvent).filter(
    ConflictEvent.latitude.is_(None)
).all()

print(f"Found {len(conflicts)} conflicts without coordinates")

# Geocode each conflict
updated = 0
not_found = 0

for conflict in conflicts:
    if not conflict.state or not conflict.lga:
        not_found += 1
        continue
    
    key = (conflict.state.strip(), conflict.lga.strip())
    
    if key in lga_coords:
        lat, lng = lga_coords[key]
        conflict.latitude = lat
        conflict.longitude = lng
        updated += 1
    else:
        # Try with just state-level geocoding
        state_key = conflict.state.strip()
        state_matches = [(s, l) for (s, l) in lga_coords.keys() if s == state_key]
        
        if state_matches:
            # Use first LGA of the state as fallback
            lat, lng = lga_coords[state_matches[0]]
            conflict.latitude = lat
            conflict.longitude = lng
            updated += 1
        else:
            not_found += 1

# Commit changes
db.commit()
db.close()

print(f"\nResults:")
print(f"  ✓ Updated: {updated}")
print(f"  ✗ Not found: {not_found}")
