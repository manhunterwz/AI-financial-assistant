import google.generativeai as genai
from sqlalchemy.orm import Session
from backend.config import GEMINI_API_KEY
from backend.services.analytics_service import get_analytics_summary

def get_chat_response(db: Session, user_id: int, message: str) -> dict:
    if not GEMINI_API_KEY:
        return {
            "response": "Gemini API key is not configured. Please set GEMINI_API_KEY in your environment.",
            "data": None
        }

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        analytics = get_analytics_summary(db, user_id)
        
        system_instruction = (
            "You are a financial AI assistant. Use only the provided context to answer the user's questions about their finances. "
            "Keep your answers concise, professional, and helpful."
        )
        
        top_cats = ", ".join([f"{c['category']} ({c['amount']})" for c in analytics['top_categories']])
        
        prompt = f"""{system_instruction}
        
Context (User's Financial Analytics):
- Total Income: {analytics['total_income']}
- Total Expenses: {analytics['total_expenses']}
- Savings: {analytics['savings']}
- Savings Rate: {analytics['savings_rate']}%
- Top Expense Categories: {top_cats}

User Message: {message}
"""
        
        response = model.generate_content(prompt)
        return {
            "response": response.text,
            "data": analytics
        }
    except Exception as e:
        return {
            "response": f"An error occurred while communicating with the AI: {str(e)}",
            "data": None
        }
