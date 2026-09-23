from sqlalchemy.orm import Session
from backend.database import Investment
from backend.models import InvestmentCreate

def get_investments(db: Session, user_id: int = 1):
    return db.query(Investment).filter(Investment.user_id == user_id).all()

def create_investment(db: Session, investment: InvestmentCreate, user_id: int = 1):
    db_investment = Investment(**investment.model_dump(), user_id=user_id)
    db.add(db_investment)
    db.commit()
    db.refresh(db_investment)
    return db_investment

def delete_investment(db: Session, investment_id: int, user_id: int = 1):
    db_investment = db.query(Investment).filter(Investment.id == investment_id, Investment.user_id == user_id).first()
    if db_investment:
        db.delete(db_investment)
        db.commit()
    return db_investment
