from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services import analytics_service
from backend.models import TransactionResponse, PredictionResponse, BudgetRecommendationResponse

router = APIRouter()

@router.get("/", response_model=List[TransactionResponse])
def get_anomalies(db: Session = Depends(get_db)):
    return analytics_service.get_anomalies(db, user_id=1)

@router.get("/predictions", response_model=PredictionResponse)
def get_predictions(db: Session = Depends(get_db)):
    predictions = analytics_service.get_predictions(db, user_id=1)
    return {"predictions": predictions}

@router.get("/recommendations", response_model=BudgetRecommendationResponse)
def get_recommendations(db: Session = Depends(get_db)):
    recommendations = analytics_service.get_budget_recommendations(db, user_id=1)
    return {"recommendations": recommendations}
