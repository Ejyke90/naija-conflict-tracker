import sys
import pandas as pd
from app.models.conflict import ConflictEvent
from app.db.database import SessionLocal

db = SessionLocal()

# Get all conflicts without coordinates
conflicts = db.query(ConflictEvent).filter(
    ConflictEvent.latitude.is_(None)
).limit(5).all()

print(f"Ungeocoded conflicts:")
for c in conflicts:
    print(f"  ID: {c.id}")
    print(f"    State: {c.state}")
    print(f"    LGA: {c.lga}")
    print(f"    Location: {c.location}")
    print()

db.close()
