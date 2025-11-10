from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict
from services.chat_service import handle_chat

router = APIRouter()

class ChatMessage(BaseModel):
    message: Optional[str] = ""
    filters: Optional[Dict[str, Optional[str]]] = {}

@router.post("/message")
def chat_message(data: ChatMessage):
    """Handle chat messages with optional filters"""
    message = data.message or ""
    filters = data.filters or {}
    
    # Extract filters from message if not provided
    if not filters and message:
        from nlp.extractor import extract_filters
        extracted_filters = extract_filters(message)
        filters = {
            "location": extracted_filters.get("location"),
            "budget": extracted_filters.get("budget"),
            "bedrooms": extracted_filters.get("bedrooms")
        }
    
    result = handle_chat(message, filters)
    return result
