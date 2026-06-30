"""
Event endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..schemas import Event, EventCreate, EventUpdate
from ..deps import DBSession
from ...models.event import Event as EventModel
from ...auth.dependencies import get_current_active_user
from ...models.operator import Operator

router = APIRouter()


@router.get("/", response_model=List[Event])
async def list_events(
    db: DBSession,
    current_user: Operator = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    drone_id: Optional[str] = None,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    """
    List events with optional filters.
    """
    query = db.query(EventModel)

    if drone_id:
        query = query.filter(EventModel.drone_id == drone_id)
    if event_type:
        query = query.filter(EventModel.event_type == event_type)
    if severity:
        query = query.filter(EventModel.severity == severity)
    if acknowledged is not None:
        if acknowledged:
            query = query.filter(EventModel.acknowledged_by.isnot(None))
        else:
            query = query.filter(EventModel.acknowledged_by.is_(None))
    if start_time:
        query = query.filter(EventModel.timestamp >= start_time)
    if end_time:
        query = query.filter(EventModel.timestamp <= end_time)

    query = query.order_by(EventModel.timestamp.desc())
    query = query.offset(skip).limit(limit)

    events = query.all()
    return events


@router.get("/{alert_id}", response_model=Event)
async def get_event(
    alert_id: str,
    db: DBSession,
    current_user: Operator = Depends(get_current_active_user)
):
    """
    Get a specific event by alert ID.
    """
    event = db.query(EventModel).filter(EventModel.alert_id == alert_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/", response_model=Event, status_code=201)
async def create_event(
    event: EventCreate,
    db: DBSession,
    current_user: Operator = Depends(get_current_active_user)
):
    """
    Create a new event (typically called by the rules engine).
    """
    # Check if alert_id already exists
    existing = db.query(EventModel).filter(EventModel.alert_id == event.alert_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Alert ID already exists")

    db_event = EventModel(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@router.put("/{alert_id}", response_model=Event)
async def update_event(
    alert_id: str,
    event: EventUpdate,
    db: DBSession,
    current_user: Operator = Depends(get_current_active_user)
):
    """
    Update an event (typically for acknowledging an alert).
    """
    db_event = db.query(EventModel).filter(EventModel.alert_id == alert_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")

    update_data = event.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_event, field, value)

    db.commit()
    db.refresh(db_event)
    return db_event


@router.delete("/{alert_id}", status_code=204)
async def delete_event(
    alert_id: str,
    db: DBSession,
    current_user: Operator = Depends(get_current_active_user)
):
    """
    Delete an event.
    """
    db_event = db.query(EventModel).filter(EventModel.alert_id == alert_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")

    db.delete(db_event)
    db.commit()
