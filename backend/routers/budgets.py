from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import BudgetCreate, BudgetResponse
from backend.services import budget_service

router = APIRouter()

@router.get("/", response_model=List[BudgetResponse])
def get_budgets(db: Session = Depends(get_db)):
    user_id = 1
    return budget_service.get_budgets(db, user_id)

@router.post("/", response_model=BudgetResponse)
def create_budget(budget: BudgetCreate, db: Session = Depends(get_db)):
    user_id = 1
    return budget_service.create_budget(db=db, user_id=user_id, budget_create_model=budget)

@router.delete("/{id}")
def delete_budget(id: int, db: Session = Depends(get_db)):
    db_budget = budget_service.delete_budget(db, id)
    if db_budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    return {"ok": True}
