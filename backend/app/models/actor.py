from sqlalchemy import BigInteger, Column, DateTime, String
from sqlalchemy.sql import func

from app.db.base_class import Base


class Actor(Base):
    """Normalized actors table (aligned with new schema)"""
    __tablename__ = "actors"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
