"""
Test validation summary endpoint
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import get_db
from app.core.config import settings

# Create test database engine
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_validation_summary_endpoint():
    """Test the validation summary endpoint returns expected structure"""
    response = client.get("/api/v1/system/validation/summary")
    
    # Should return 200 OK
    assert response.status_code == 200
    
    data = response.json()
    
    # Check required fields exist
    required_fields = [
        "pendingCount", "isUrgent", "highPriorityCount", 
        "lastActivity", "totalVerified", "oldestItem"
    ]
    
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    # Check data types
    assert isinstance(data["pendingCount"], int)
    assert isinstance(data["isUrgent"], bool)
    assert isinstance(data["highPriorityCount"], int)
    assert isinstance(data["totalVerified"], int)
    
    # Check timestamps are strings or None
    assert data["lastActivity"] is None or isinstance(data["lastActivity"], str)
    assert data["oldestItem"] is None or isinstance(data["oldestItem"], str)
    
    # Check status field
    assert "status" in data
    assert data["status"] in ["ok", "error", "no_data"]


def test_validation_summary_with_mock_view():
    """Test validation summary when the view exists and has data"""
    db = TestingSessionLocal()
    
    try:
        # Create a mock validation_summary view for testing
        # This assumes the view already exists in Neon PostgreSQL
        result = db.execute(text("SELECT * FROM validation_summary LIMIT 1")).first()
        
        # If the view exists, test the endpoint
        response = client.get("/api/v1/system/validation/summary")
        assert response.status_code == 200
        
        data = response.json()
        
        if data["status"] == "ok":
            # Verify data makes sense when view has data
            assert data["pendingCount"] >= 0
            assert data["totalVerified"] >= 0
            assert data["highPriorityCount"] >= 0
            
    except Exception as e:
        # If view doesn't exist, endpoint should return graceful degradation
        response = client.get("/api/v1/system/validation/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] in ["error", "no_data"]
        
    finally:
        db.close()


def test_validation_summary_performance():
    """Test that the endpoint responds quickly (should be fast due to Neon view)"""
    import time
    
    start_time = time.time()
    response = client.get("/api/v1/system/validation/summary")
    end_time = time.time()
    
    # Should respond within 2 seconds (Neon view should be very fast)
    response_time = end_time - start_time
    assert response_time < 2.0, f"Endpoint too slow: {response_time:.2f}s"
    assert response.status_code == 200


if __name__ == "__main__":
    # Run basic test
    test_validation_summary_endpoint()
    test_validation_summary_performance()
    print("✅ Validation summary endpoint tests passed!")
