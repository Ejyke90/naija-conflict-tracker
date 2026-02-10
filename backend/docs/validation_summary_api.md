# Validation Summary API Endpoint

## Overview

The Validation Summary API provides a high-performance endpoint that serves pre-computed summary data from a Neon PostgreSQL view. This endpoint replaces the complex System Heartbeat with a optimized solution that abstracts away the heavy mathematical computations.

## Endpoint

```
GET /api/v1/system/validation/summary
```

## Authentication

**Public Endpoint** - No authentication required for optimal performance.

## Response Format

```json
{
  "pendingCount": 15,
  "isUrgent": true,
  "highPriorityCount": 8,
  "lastActivity": "2026-02-10T10:30:00Z",
  "totalVerified": 1247,
  "oldestItem": "2026-02-08T14:22:00Z",
  "status": "ok",
  "timestamp": "2026-02-10T12:13:45.123Z"
}
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `pendingCount` | integer | Number of items pending validation |
| `isUrgent` | boolean | Urgent status logic based on business rules |
| `highPriorityCount` | integer | Count of high-priority pending items |
| `lastActivity` | string \| null | ISO timestamp of last validation activity |
| `totalVerified` | integer | Total number of verified items |
| `oldestItem` | string \| null | ISO timestamp of oldest pending item |
| `status` | string | Response status: "ok", "error", or "no_data" |
| `timestamp` | string | ISO timestamp of the response |

## Error Handling

The endpoint implements graceful degradation:

### No Data Available
```json
{
  "pendingCount": 0,
  "isUrgent": false,
  "highPriorityCount": 0,
  "lastActivity": null,
  "totalVerified": 0,
  "oldestItem": null,
  "status": "no_data",
  "message": "Validation summary view is empty or not accessible"
}
```

### Database Error
```json
{
  "pendingCount": 0,
  "isUrgent": false,
  "highPriorityCount": 0,
  "lastActivity": null,
  "totalVerified": 0,
  "oldestItem": null,
  "status": "error",
  "message": "Unable to retrieve validation summary",
  "error_code": "VALIDATION_SUMMARY_ERROR",
  "timestamp": "2026-02-10T12:13:45.123Z"
}
```

## Performance

- **Target Response Time:** < 500ms
- **Cache Recommendation:** 2 minutes
- **Source:** Neon PostgreSQL validation_summary view
- **Optimization:** Pre-computed aggregations in PostgreSQL view

## Usage Examples

### JavaScript/TypeScript
```javascript
const response = await fetch('/api/v1/system/validation/summary');
const data = await response.json();

if (data.status === 'ok') {
  console.log(`Pending items: ${data.pendingCount}`);
  console.log(`Urgent: ${data.isUrgent}`);
  console.log(`Total verified: ${data.totalVerified}`);
}
```

### Python
```python
import requests

response = requests.get('http://localhost:8000/api/v1/system/validation/summary')
data = response.json()

if data['status'] == 'ok':
    print(f"Pending items: {data['pendingCount']}")
    print(f"Urgent: {data['isUrgent']}")
    print(f"Total verified: {data['totalVerified']}")
```

### cURL
```bash
curl http://localhost:8000/api/v1/system/validation/summary
```

## Testing

Run the provided test script:
```bash
./test_validation_endpoint.sh
```

Or run the Python tests:
```bash
python tests/test_validation_summary.py
```

## Implementation Details

### Backend Implementation (FastAPI)
```python
@router.get("/validation/summary")
async def get_validation_summary(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT * FROM validation_summary")).first()
        
        if not result:
            return { /* default values */ }
        
        return {
            "pendingCount": result[0],
            "isUrgent": bool(result[1]),
            "highPriorityCount": result[2],
            "lastActivity": result[3].isoformat() if result[3] else None,
            "totalVerified": result[4],
            "oldestItem": result[5].isoformat() if result[5] else None,
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return { /* error handling */ }
```

### Neon PostgreSQL View
The endpoint queries a pre-computed view in Neon PostgreSQL:
```sql
CREATE VIEW validation_summary AS
SELECT 
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_count,
    COUNT(CASE WHEN priority = 'high' AND status = 'pending' THEN 1 END) > 5 as is_urgent_logic,
    COUNT(CASE WHEN priority = 'high' AND status = 'pending' THEN 1 END) as high_priority_count,
    MAX(created_at) FILTER (WHERE status = 'validated') as last_validation,
    COUNT(CASE WHEN status = 'validated' THEN 1 END) as verified_count,
    MIN(created_at) FILTER (WHERE status = 'pending') as oldest_pending
FROM validation_table;
```

## Frontend Integration

### React Component Example
```typescript
interface ValidationSummary {
  pendingCount: number;
  isUrgent: boolean;
  highPriorityCount: number;
  lastActivity: string | null;
  totalVerified: number;
  oldestItem: string | null;
  status: 'ok' | 'error' | 'no_data';
}

const ValidationDashboard: React.FC = () => {
  const [summary, setSummary] = useState<ValidationSummary | null>(null);
  
  useEffect(() => {
    fetch('/api/v1/system/validation/summary')
      .then(res => res.json())
      .then(setSummary);
  }, []);
  
  if (!summary) return <div>Loading...</div>;
  
  return (
    <div>
      <h2>Validation Summary</h2>
      <p>Pending: {summary.pendingCount}</p>
      <p>Urgent: {summary.isUrgent ? 'Yes' : 'No'}</p>
      <p>Total Verified: {summary.totalVerified}</p>
    </div>
  );
};
```

## Deployment Notes

1. **Neon PostgreSQL**: Ensure the validation_summary view exists in your Neon database
2. **Environment Variables**: No additional environment variables required
3. **Monitoring**: Monitor endpoint response times and error rates
4. **Caching**: Consider implementing Redis caching for additional performance

## Related Endpoints

- `/api/v1/system/heartbeat` - Comprehensive system heartbeat
- `/api/v1/system/metrics` - System performance metrics
- `/api/v1/analytics/stats` - Public statistics
