#!/usr/bin/env python3
from app.db.database import get_db
from app.models.conflict import ConflictEvent
from datetime import datetime, timedelta
import random

db = next(get_db())

# Clear existing data
db.query(ConflictEvent).delete()

# Add sample data for the last 30 days
states = ['Lagos', 'Kano', 'Abuja', 'Rivers', 'Kaduna', 'Oyo', 'Enugu', 'Edo']
event_types = ['Armed Conflict', 'Communal Clash', 'Banditry', 'Kidnapping']

for i in range(50):
    event_date = datetime.now().date() - timedelta(days=random.randint(0, 30))
    event = ConflictEvent(
        event_date=event_date,
        year=event_date.year,
        month=event_date.month,
        state=random.choice(states),
        lga=f'LGA{random.randint(1,20)}',
        event_type=random.choice(event_types),
        fatalities=random.randint(0, 5),
        injuries=random.randint(0, 10),
        verified=True
    )
    db.add(event)

db.commit()
print('✅ Added 50 sample conflict events')