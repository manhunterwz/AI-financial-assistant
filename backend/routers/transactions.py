from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import TransactionCreate, TransactionResponse
from backend.services import transaction_service
from fastapi import File, UploadFile
import google.generativeai as genai
from PIL import Image
import io
import json
from backend.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

router = APIRouter()

@router.get("/", response_model=List[TransactionResponse])
def get_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return transaction_service.get_transactions(db, skip=skip, limit=limit)

@router.post("/", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    return transaction_service.create_transaction(db=db, transaction_create_model=transaction)

@router.delete("/{id}")
def delete_transaction(id: int, db: Session = Depends(get_db)):
    db_trans = transaction_service.delete_transaction(db, id)
    if db_trans is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"ok": True}

@router.post("/scan-receipt")
async def scan_receipt(file: UploadFile = File(...)):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        image = Image.open(io.BytesIO(await file.read()))
        prompt = "Analyze this receipt/bill. Extract the total amount, description/merchant name, and date (YYYY-MM-DD). Return ONLY valid JSON in this format: {\"amount\": float, \"description\": \"string\", \"date\": \"string\"}. No markdown formatting."
        response = model.generate_content([prompt, image])
        
        # Clean markdown if present
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        data = json.loads(text)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to scan receipt: {str(e)}")
