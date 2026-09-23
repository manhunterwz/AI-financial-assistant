from sqlalchemy.orm import Session
from backend.database import Budget
from backend.models import BudgetCreate

def get_budgets(db: Session, user_id: int):
    return db.query(Budget).filter(Budget.user_id == user_id).all()

def create_budget(db: Session, user_id: int, budget_create_model: BudgetCreate):
    db_budget = Budget(
        user_id=user_id,
        category=budget_create_model.category,
        budget_limit=budget_create_model.budget_limit,
        month=budget_create_model.month
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

def delete_budget(db: Session, id: int):
    db_budget = db.query(Budget).filter(Budget.id == id).first()
    if db_budget:
        db.delete(db_budget)
        db.commit()
    return db_budget
