import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ML_DIR = BASE_DIR / "ml" / "trained_models"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
ML_DIR.mkdir(parents=True, exist_ok=True)

# Database
DATABASE_URL = f"sqlite:///{DATA_DIR / 'financial_assistant.db'}"

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Default settings
DEFAULT_CURRENCY = "INR"
SUPPORTED_CURRENCIES = ["INR", "USD", "EUR", "GBP", "JPY", "AUD", "CAD"]
CURRENCY_SYMBOLS = {
    "INR": "₹", "USD": "$", "EUR": "€", "GBP": "£",
    "JPY": "¥", "AUD": "A$", "CAD": "C$"
}

# Expense categories
EXPENSE_CATEGORIES = [
    "Food & Dining", "Transport", "Shopping", "Entertainment",
    "Utilities", "Rent", "Healthcare", "Education",
    "Groceries", "Personal Care", "Travel", "Subscriptions",
    "Gifts & Donations", "Insurance", "Miscellaneous"
]

INCOME_CATEGORIES = [
    "Salary", "Freelance", "Investment", "Business",
    "Rental Income", "Refund", "Other Income"
]
