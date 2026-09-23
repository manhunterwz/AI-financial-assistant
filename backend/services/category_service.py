from sqlalchemy.orm import Session
from backend.database import Category

def get_categories(db: Session, type: str = None):
    query = db.query(Category)
    if type:
        query = query.filter(Category.type == type)
    return query.all()
