"""
Drone model.
"""

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from ..db.base import Base


class Drone(Base):
    """Drone model representing a drone in the system."""
    
    __tablename__ = "drones"
    
    id = Column(String, primary_key=True, index=True)  # e.g., "drone-01"
    name = Column(String, nullable=False)  # Human-readable name
    stream_url = Column(String, nullable=False)  # RTSP/RTMP/SRT URL
    link_type = Column(String, nullable=False)  # "LOS" or "BLOS"
    status = Column(String, default="offline")  # "online", "offline", "error"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Drone(id={self.id}, name={self.name}, status={self.status})>"
