from sqlalchemy.orm import Session
from backend.database import Loan
from backend.models import LoanCreate

def get_loans(db: Session, user_id: int = 1):
    return db.query(Loan).filter(Loan.user_id == user_id).all()

def create_loan(db: Session, loan: LoanCreate, user_id: int = 1):
    db_loan = Loan(**loan.model_dump(), user_id=user_id)
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan

def delete_loan(db: Session, loan_id: int, user_id: int = 1):
    db_loan = db.query(Loan).filter(Loan.id == loan_id, Loan.user_id == user_id).first()
    if db_loan:
        db.delete(db_loan)
        db.commit()
    return db_loan
