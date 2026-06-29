"""
Drone endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..schemas import Drone, DroneCreate, DroneUpdate
from ..deps import DBSession
from ...models.drone import Drone as DroneModel
from ...auth.dependencies import get_current_active_user
from ...models.operator import Operator

router = APIRouter()


@router.get("/", response_model=List[Drone])
async def list_drones(
    current_user: Operator = Depends(get_current_active_user),
    db: DBSession = Depends()
):
    """
    List all drones.
    """
    drones = db.query(DroneModel).all()
    return drones


@router.get("/{drone_id}", response_model=Drone)
async def get_drone(
    drone_id: str,
    current_user: Operator = Depends(get_current_active_user),
    db: DBSession = Depends()
):
    """
    Get a specific drone by ID.
    """
    drone = db.query(DroneModel).filter(DroneModel.id == drone_id).first()
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")
    return drone


@router.post("/", response_model=Drone, status_code=201)
async def create_drone(
    drone: DroneCreate,
    current_user: Operator = Depends(get_current_active_user),
    db: DBSession = Depends()
):
    """
    Create a new drone.
    """
    # Check if drone already exists
    existing = db.query(DroneModel).filter(DroneModel.id == drone.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Drone ID already exists")

    db_drone = DroneModel(**drone.model_dump())
    db.add(db_drone)
    db.commit()
    db.refresh(db_drone)
    return db_drone


@router.put("/{drone_id}", response_model=Drone)
async def update_drone(
    drone_id: str,
    drone: DroneUpdate,
    current_user: Operator = Depends(get_current_active_user),
    db: DBSession = Depends()
):
    """
    Update a drone.
    """
    db_drone = db.query(DroneModel).filter(DroneModel.id == drone_id).first()
    if not db_drone:
        raise HTTPException(status_code=404, detail="Drone not found")

    update_data = drone.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_drone, field, value)

    db.commit()
    db.refresh(db_drone)
    return db_drone


@router.delete("/{drone_id}", status_code=204)
async def delete_drone(
    drone_id: str,
    current_user: Operator = Depends(get_current_active_user),
    db: DBSession = Depends()
):
    """
    Delete a drone.
    """
    db_drone = db.query(DroneModel).filter(DroneModel.id == drone_id).first()
    if not db_drone:
        raise HTTPException(status_code=404, detail="Drone not found")

    db.delete(db_drone)
    db.commit()
