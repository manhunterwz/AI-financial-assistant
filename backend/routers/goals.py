from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import SavingsGoalCreate, SavingsGoalResponse
from backend.services import goal_service

router = APIRouter()

@router.get("/", response_model=List[SavingsGoalResponse])
def get_goals(db: Session = Depends(get_db)):
    return goal_service.get_goals(db)

@router.post("/", response_model=SavingsGoalResponse)
def create_goal(goal: SavingsGoalCreate, db: Session = Depends(get_db)):
    return goal_service.create_goal(db, goal)

@router.delete("/{id}")
def delete_goal(id: int, db: Session = Depends(get_db)):
    db_goal = goal_service.delete_goal(db, id)
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"ok": True}
