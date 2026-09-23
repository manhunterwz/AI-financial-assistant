from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import LoanCreate, LoanResponse
from backend.services import loan_service

router = APIRouter()

@router.get("/", response_model=List[LoanResponse])
def get_loans(db: Session = Depends(get_db)):
    return loan_service.get_loans(db)

@router.post("/", response_model=LoanResponse)
def create_loan(loan: LoanCreate, db: Session = Depends(get_db)):
    return loan_service.create_loan(db, loan)

@router.delete("/{id}")
def delete_loan(id: int, db: Session = Depends(get_db)):
    db_loan = loan_service.delete_loan(db, id)
    if not db_loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return {"ok": True}
