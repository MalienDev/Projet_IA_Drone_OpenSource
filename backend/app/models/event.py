"""
Event model.
"""

from sqlalchemy import Column, String, Float, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..db.base import Base


class Event(Base):
    """Event model representing a detection/alert event."""
    
    __tablename__ = "events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(String, unique=True, index=True, nullable=False)  # UUID-v4 string
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    drone_id = Column(String, ForeignKey("drones.id"), nullable=False, index=True)
    event_type = Column(String, nullable=False, index=True)  # weapon_suspected, intrusion, crowd, etc.
    severity = Column(String, nullable=False, index=True)  # low, medium, high, critical
    confidence = Column(Float, nullable=False)
    bbox = Column(JSON, nullable=False)  # [x1, y1, x2, y2]
    track_id = Column(String, nullable=True, index=True)
    zone_id = Column(String, ForeignKey("zones.id"), nullable=True, index=True)
    geo = Column(JSON, nullable=True)  # {"lat": null, "lon": null}
    snapshot_path = Column(String, nullable=True)
    clip_path = Column(String, nullable=True)
    requires_operator_ack = Column(Boolean, default=True)
    acknowledged_by = Column(String, ForeignKey("operators.username"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Event(alert_id={self.alert_id}, type={self.event_type}, severity={self.severity})>"
