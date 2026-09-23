from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import ChatMessage, ChatResponse
from backend.services.chatbot_service import get_chat_response

router = APIRouter()

@router.post("/", response_model=ChatResponse)
def chat_with_bot(chat_message: ChatMessage, db: Session = Depends(get_db)):
    # Assuming user_id=1 as default for single-user environment
    user_id = 1 
    result = get_chat_response(db, user_id, chat_message.message)
    return ChatResponse(response=result["response"], data=result.get("data"))
