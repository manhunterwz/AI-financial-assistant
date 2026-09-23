from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import TransactionCreate, TransactionResponse
from backend.services import transaction_service

router = APIRouter()

@router.get("/", response_model=List[TransactionResponse])
def get_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return transaction_service.get_transactions(db, skip=skip, limit=limit)

@router.post("/", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    return transaction_service.create_transaction(db=db, transaction_create_model=transaction)

@router.delete("/{id}")
def delete_transaction(id: int, db: Session = Depends(get_db)):
    db_trans = transaction_service.delete_transaction(db, id)
    if db_trans is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"ok": True}
