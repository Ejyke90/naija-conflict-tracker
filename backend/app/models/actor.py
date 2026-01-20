from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Actor(Base):
    __tablename__ = "actors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    type = Column(String(50), index=True)  # armed_group, military, police, militia, bandits
    ideology = Column(String(100))
    active_since = Column(DateTime)
    description = Column(Text)

    # Removed conflicts relationship
