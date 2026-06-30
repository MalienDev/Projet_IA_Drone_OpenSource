"""
Zone endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..schemas import Zone, ZoneCreate, ZoneUpdate
from ..deps import DBSession
from ...models.zone import Zone as ZoneModel
from ...auth.dependencies import get_current_active_user
from ...models.operator import Operator

router = APIRouter()


@router.get("/", response_model=List[Zone])
async def list_zones(
    db: DBSession,
    current_user: Operator = Depends(get_current_active_user)
):
    """
    List all zones.
    """
    zones = db.query(ZoneModel).all()
    return zones


@router.get("/{zone_id}", response_model=Zone)
async def get_zone(
    zone_id: str,
    db: DBSession,
    current_user: Operator = Depends(get_current_active_user)
):
    """
    Get a specific zone by ID.
    """
    zone = db.query(ZoneModel).filter(ZoneModel.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone


@router.post("/", response_model=Zone, status_code=201)
async def create_zone(
    zone: ZoneCreate,
    db: DBSession,
    current_user: Operator = Depends(get_current_active_user)
):
    """
    Create a new zone.
    """
    # Check if zone already exists
    existing = db.query(ZoneModel).filter(ZoneModel.id == zone.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Zone ID already exists")

    db_zone = ZoneModel(**zone.model_dump())
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    return db_zone


@router.put("/{zone_id}", response_model=Zone)
async def update_zone(
    zone_id: str,
    zone: ZoneUpdate,
    db: DBSession,
    current_user: Operator = Depends(get_current_active_user)
):
    """
    Update a zone.
    """
    db_zone = db.query(ZoneModel).filter(ZoneModel.id == zone_id).first()
    if not db_zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    update_data = zone.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_zone, field, value)

    db.commit()
    db.refresh(db_zone)
    return db_zone


@router.delete("/{zone_id}", status_code=204)
async def delete_zone(
    zone_id: str,
    db: DBSession,
    current_user: Operator = Depends(get_current_active_user)
):
    """
    Delete a zone.
    """
    db_zone = db.query(ZoneModel).filter(ZoneModel.id == zone_id).first()
    if not db_zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    db.delete(db_zone)
    db.commit()
