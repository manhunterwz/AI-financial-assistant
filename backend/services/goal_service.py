from sqlalchemy.orm import Session
from backend.database import SavingsGoal
from backend.models import SavingsGoalCreate

def get_goals(db: Session, user_id: int = 1):
    return db.query(SavingsGoal).filter(SavingsGoal.user_id == user_id).all()

def create_goal(db: Session, goal: SavingsGoalCreate, user_id: int = 1):
    db_goal = SavingsGoal(**goal.model_dump(), user_id=user_id)
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

def delete_goal(db: Session, goal_id: int, user_id: int = 1):
    db_goal = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id, SavingsGoal.user_id == user_id).first()
    if db_goal:
        db.delete(db_goal)
        db.commit()
    return db_goal
