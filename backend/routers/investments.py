from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import InvestmentCreate, InvestmentResponse
from backend.services import investment_service

router = APIRouter()

@router.get("/", response_model=List[InvestmentResponse])
def get_investments(db: Session = Depends(get_db)):
    return investment_service.get_investments(db)

@router.post("/", response_model=InvestmentResponse)
def create_investment(investment: InvestmentCreate, db: Session = Depends(get_db)):
    return investment_service.create_investment(db, investment)

@router.delete("/{id}")
def delete_investment(id: int, db: Session = Depends(get_db)):
    db_investment = investment_service.delete_investment(db, id)
    if not db_investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    return {"ok": True}
