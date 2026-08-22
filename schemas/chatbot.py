from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, json_schema_extra={"example": "I want to go from Hinjawadi to Pune Station. What should I know?"})
    conversation_id: Optional[str] = None
    user_location: Optional[Dict[str, float]] = None


class ChatIntent(BaseModel):
    intent: str
    origin: Optional[str] = None
    destination: Optional[str] = None
    entities: Dict[str, Any] = {}
    confidence: float = 0.9


class ChatContext(BaseModel):
    intent: str
    route: Optional[Dict[str, Any]] = None
    weather: Optional[Dict[str, Any]] = None
    projects: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    infrastructure: List[Dict[str, Any]] = []
    transport: List[Dict[str, Any]] = []
    officer: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    response: str
    intent: str
    conversation_id: str
    context_used: Dict[str, Any]
    precautions: List[str] = []
    disclaimer: str = "This response is grounded in verified Pune Municipal and Smart City infrastructure datasets. Predictions represent risk probabilities and not guaranteed occurrences."
