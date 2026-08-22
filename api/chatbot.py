from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.chatbot import ChatRequest, ChatResponse
from app.services.chatbot_service import chatbot_service

router = APIRouter(prefix="/chat", tags=["Citizen & Officer AI Chatbot"])


@router.post("", response_model=ChatResponse, summary="Natural language smart city assistant grounded on verified datasets")
async def chat_with_assistant(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Conversational AI assistant powered by Google Gemini.
    Features strict anti-hallucination architecture: Gemini receives structured factual context
    from PMC datasets, sensors, weather, and commute routes.
    """
    return await chatbot_service.handle_message(db, payload)
