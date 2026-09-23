from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from backend.database import get_db
from backend.services import category_service

router = APIRouter()

@router.get("/")
def get_categories(type: Optional[str] = None, db: Session = Depends(get_db)):
    categories = category_service.get_categories(db, type)
    # Convert SQLAlchemy models to dicts for FastAPI serialization if no response model is provided
    return [{"id": c.id, "name": c.name, "type": c.type, "icon": c.icon} for c in categories]
