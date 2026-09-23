from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import Transaction

def get_analytics_summary(db: Session, user_id: int):
    income = db.query(func.sum(Transaction.amount)).filter(Transaction.user_id == user_id, Transaction.type == 'income').scalar() or 0.0
    expenses = db.query(func.sum(Transaction.amount)).filter(Transaction.user_id == user_id, Transaction.type == 'expense').scalar() or 0.0
    
    savings = income - expenses
    savings_rate = (savings / income) * 100 if income > 0 else 0.0
    
    top_cat_data = db.query(
        Transaction.category, func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == user_id, Transaction.type == 'expense'
    ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).limit(5).all()
    
    top_categories = [{"category": row[0], "amount": float(row[1])} for row in top_cat_data]
    
    # SQLite strftime
    monthly_data = db.query(
        func.strftime('%Y-%m', Transaction.transaction_date).label('month'),
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == user_id, Transaction.type == 'expense'
    ).group_by('month').order_by('month').all()
    
    monthly_trend = [{"month": row[0], "amount": float(row[1])} for row in monthly_data if row[0]]
    
    return {
        "total_income": float(income),
        "total_expenses": float(expenses),
        "savings": float(savings),
        "savings_rate": float(savings_rate),
        "top_categories": top_categories,
        "monthly_trend": monthly_trend
    }

from ml.expense_predictor import ExpensePredictor
from ml.budget_recommender import BudgetRecommender
import pandas as pd

predictor = ExpensePredictor()
recommender = BudgetRecommender()

def get_anomalies(db: Session, user_id: int):
    return db.query(Transaction).filter(
        Transaction.user_id == user_id, 
        Transaction.is_anomaly == True
    ).order_by(Transaction.anomaly_score.asc()).limit(20).all()

def get_predictions(db: Session, user_id: int):
    expense_data = db.query(
        Transaction.category,
        func.strftime('%Y-%m', Transaction.transaction_date).label('month')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense'
    ).all()
    
    cat_months = {}
    for row in expense_data:
        cat = row.category
        month = row.month
        if cat not in cat_months:
            cat_months[cat] = set()
        cat_months[cat].add(month)
        
    predictions = {}
    for cat, months in cat_months.items():
        next_month_index = len(months)
        pred_amount = predictor.predict(cat, next_month_index)
        predictions[cat] = float(pred_amount)
        
    return predictions

def get_budget_recommendations(db: Session, user_id: int):
    expense_data = db.query(
        Transaction.transaction_date.label('date'),
        Transaction.category,
        Transaction.amount
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense'
    ).all()
    
    if not expense_data:
        return {}
        
    df = pd.DataFrame([
        {'date': row.date, 'category': row.category, 'amount': row.amount} 
        for row in expense_data
    ])
    
    recommendations = recommender.recommend(df)
    return recommendations
