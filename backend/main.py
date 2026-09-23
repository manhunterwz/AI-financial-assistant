from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database and create tables
    init_db()
    yield
    # Cleanup resources here if needed

app = FastAPI(title="AI Financial Assistant", lifespan=lifespan)

# Allow CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.routers import transactions, analytics, budgets, categories, chat, anomalies, investments, loans, goals
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(budgets.router, prefix="/api/budgets", tags=["Budgets"])
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chatbot"])
app.include_router(anomalies.router, prefix="/api/ml", tags=["ML Insights"])
app.include_router(investments.router, prefix="/api/investments", tags=["Investments"])
app.include_router(loans.router, prefix="/api/loans", tags=["Loans"])
app.include_router(goals.router, prefix="/api/goals", tags=["Goals"])

@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "project": "AI Financial Assistant",
        "version": "1.0.0"
    }
