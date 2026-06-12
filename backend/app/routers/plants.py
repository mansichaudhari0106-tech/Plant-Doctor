from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Plant
from app.models.schemas import PlantCreate, PlantOut

router = APIRouter(prefix="/plants", tags=["plants"])


@router.post("", response_model=PlantOut, status_code=201)
def create_plant(payload: PlantCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    plant = Plant(
        owner_id=user.id,
        name=payload.name,
        species=payload.species,
        location=payload.location,
        status="unknown",
    )
    db.add(plant)
    db.commit()
    db.refresh(plant)
    return plant


@router.get("", response_model=List[PlantOut])
def list_plants(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Plant).filter(Plant.owner_id == user.id).all()


@router.get("/{plant_id}", response_model=PlantOut)
def get_plant(plant_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    plant = db.query(Plant).filter(Plant.id == plant_id, Plant.owner_id == user.id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant


@router.delete("/{plant_id}", status_code=204)
def delete_plant(plant_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    plant = db.query(Plant).filter(Plant.id == plant_id, Plant.owner_id == user.id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    db.delete(plant)
    db.commit()
    return None
