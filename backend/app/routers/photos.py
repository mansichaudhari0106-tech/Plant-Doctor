import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.models import User, Plant, Photo

router = APIRouter(prefix="/photos", tags=["photos"])


@router.get("/{photo_id}")
def get_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Serve a photo only to its owner — private, authenticated access."""
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    plant = db.query(Plant).filter(
        Plant.id == photo.plant_id,
        Plant.owner_id == user.id
    ).first()
    if not plant:
        raise HTTPException(status_code=403, detail="Access denied")

    if not os.path.exists(photo.filepath):
        raise HTTPException(status_code=404, detail="Photo file not found")

    return FileResponse(photo.filepath, media_type="image/jpeg")
