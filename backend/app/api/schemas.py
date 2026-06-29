"""
Pydantic schemas for API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Drone schemas
class DroneBase(BaseModel):
    name: str
    stream_url: str
    link_type: str = Field(..., pattern="^(LOS|BLOS)$")
    status: str = "offline"


class DroneCreate(DroneBase):
    id: str


class DroneUpdate(BaseModel):
    name: Optional[str] = None
    stream_url: Optional[str] = None
    link_type: Optional[str] = Field(None, pattern="^(LOS|BLOS)$")
    status: Optional[str] = None


class Drone(DroneBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Zone schemas
class ZoneBase(BaseModel):
    name: str
    polygon_geojson: dict
    zone_type: str = Field(..., pattern="^(INTRUSION|CROWD|SAFE)$")
    rules_json: Optional[dict] = None


class ZoneCreate(ZoneBase):
    id: str


class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    polygon_geojson: Optional[dict] = None
    zone_type: Optional[str] = Field(None, pattern="^(INTRUSION|CROWD|SAFE)$")
    rules_json: Optional[dict] = None


class Zone(ZoneBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Event schemas
class EventBase(BaseModel):
    alert_id: str
    timestamp: datetime
    drone_id: str
    event_type: str
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    confidence: float = Field(..., ge=0.0, le=1.0)
    bbox: List[float] = Field(..., min_length=4, max_length=4)
    track_id: Optional[str] = None
    zone_id: Optional[str] = None
    geo: Optional[dict] = None
    snapshot_path: Optional[str] = None
    clip_path: Optional[str] = None
    requires_operator_ack: bool = True


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None


class Event(EventBase):
    id: str
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Operator schemas
class OperatorBase(BaseModel):
    username: str
    role: str = "operator"


class OperatorCreate(OperatorBase):
    password_hash: str


class OperatorUpdate(BaseModel):
    password_hash: Optional[str] = None
    role: Optional[str] = None


class Operator(OperatorBase):
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Health check schema
class HealthResponse(BaseModel):
    status: str
    database: str
    redis: str


# Authentication schemas
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str
