"""
Database setup endpoint for Railway deployment
"""

from fastapi import APIRouter, HTTPException
from app.db.database import engine
from app.db.base import Base

router = APIRouter(prefix="/api/setup", tags=["setup"])

@router.post("/create-tables")
async def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        return {
            "status": "success",
            "message": "Database tables created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create tables: {str(e)}")

@router.get("/check-tables")
async def check_tables():
    """Check if tables exist"""
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return {
            "status": "success",
            "tables": tables,
            "conflicts_table_exists": "conflicts" in tables
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check tables: {str(e)}")
