from sqlalchemy.orm import Session
from backend.database import Transaction
from backend.models import TransactionCreate
from ml.categorizer import ExpenseCategorizer
from ml.anomaly_detector import AnomalyDetector

categorizer = ExpenseCategorizer()
detector = AnomalyDetector()

def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Transaction).order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()

def get_transaction_by_id(db: Session, id: int):
    return db.query(Transaction).filter(Transaction.id == id).first()

def create_transaction(db: Session, transaction_create_model: TransactionCreate):
    category = transaction_create_model.category
    if not category:
        category, confidence = categorizer.predict(transaction_create_model.description)

    is_anomaly = False
    anomaly_score = 0.0

    if transaction_create_model.type == 'expense':
        is_anomaly, anomaly_score = detector.predict(
            float(transaction_create_model.amount), 
            str(transaction_create_model.transaction_date)
        )

    db_transaction = Transaction(
        user_id=1,  # Demo User hardcoded
        amount=transaction_create_model.amount,
        type=transaction_create_model.type,
        category=category,
        description=transaction_create_model.description,
        transaction_date=transaction_create_model.transaction_date,
        is_anomaly=is_anomaly,
        anomaly_score=anomaly_score
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, id: int):
    db_transaction = get_transaction_by_id(db, id)
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
    return db_transaction
