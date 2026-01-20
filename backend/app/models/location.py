from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from app.db.base_class import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20), nullable=False, index=True)  # state, lga, community
    name = Column(String(200), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("locations.id"), index=True)
    boundary = Column(Geography("MULTIPOLYGON, 4326"), nullable=True)
    population = Column(Integer)
    poverty_rate = Column(Float)
    unemployment_rate = Column(Float)
    extra_data = Column(JSONB)

    # Self-referential relationship for hierarchy
    parent = relationship("Location", remote_side=[id], back_populates="children")
    children = relationship("Location", back_populates="parent")
