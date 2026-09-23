from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import AnalyticsSummary
from backend.services import analytics_service

router = APIRouter()

@router.get("/", response_model=AnalyticsSummary)
def get_analytics(db: Session = Depends(get_db)):
    user_id = 1
    return analytics_service.get_analytics_summary(db, user_id)
