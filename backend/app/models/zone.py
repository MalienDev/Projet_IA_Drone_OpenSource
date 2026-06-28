"""
Zone model.
"""

from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.sql import func
from ..db.base import Base


class Zone(Base):
    """Zone model representing a surveillance zone."""
    
    __tablename__ = "zones"
    
    id = Column(String, primary_key=True, index=True)  # e.g., "zone-perimetre-nord"
    name = Column(String, nullable=False)  # Human-readable name
    polygon_geojson = Column(JSON, nullable=False)  # GeoJSON polygon
    zone_type = Column(String, nullable=False)  # "INTRUSION", "CROWD", "SAFE"
    rules_json = Column(JSON, nullable=True)  # Zone-specific rules (thresholds, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Zone(id={self.id}, name={self.name}, type={self.zone_type})>"
