from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

class TransactionCreate(BaseModel):
    amount: float
    type: str
    category: Optional[str] = None
    description: str
    transaction_date: date

class TransactionResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    type: str
    category: Optional[str] = None
    description: str
    transaction_date: date
    is_anomaly: bool
    anomaly_score: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TransactionListResponse(BaseModel):
    items: List[TransactionResponse]
    total_count: int

    model_config = ConfigDict(from_attributes=True)

class BudgetCreate(BaseModel):
    category: str
    budget_limit: float
    month: str

class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category: str
    budget_limit: float
    month: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SavingsGoalCreate(BaseModel):
    goal_name: str
    target_amount: float
    target_date: Optional[date] = None

class SavingsGoalResponse(BaseModel):
    id: int
    user_id: int
    goal_name: str
    target_amount: float
    current_amount: float
    target_date: Optional[date] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    name: str
    email: str
    monthly_income: float = 0.0
    currency: str = "INR"

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    monthly_income: float
    currency: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    data: Optional[dict] = None

class AnalyticsSummary(BaseModel):
    total_income: float
    total_expenses: float
    savings: float
    savings_rate: float
    top_categories: List[dict]
    monthly_trend: List[dict]

class AnomalyAlert(BaseModel):
    transaction_id: int
    amount: float
    category: str
    description: str
    anomaly_score: float
    message: str

class PredictionResponse(BaseModel):
    predictions: dict  # {category: predicted_amount}

class BudgetRecommendationResponse(BaseModel):
    recommendations: dict  # {category: recommended_budget}
