import pytest
from fastapi.testclient import TestClient
from app.main import app  
from app.db.database import engine  

client = TestClient(app)

def test_agent_routing():
    response = client.get('/api/v1/route_agent?query=data_science')
    assert response.status_code == 200
    assert response.json()['routed_agent'] == 'DATA_SCIENCE_AGENT'

def test_data_ingestion():
    # Simulate data check, e.g., query database for duplicates
    import pandas as pd
    df = pd.read_sql_query('SELECT COUNT(*) FROM conflict_articles GROUP BY title HAVING COUNT(*) > 1', engine)
    assert df.empty, 'Duplicates found in conflict_articles'

if __name__ == '__main__':
    pytest.main()
