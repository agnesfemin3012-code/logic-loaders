from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.models.prediction import PredictionType


class PredictionBase(BaseModel):
    asset_id: int
    prediction_type: PredictionType
    probability: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence: float = Field(0.75, ge=0.0, le=1.0)
    predicted_failure_window: Optional[str] = None
    estimated_rul_min: Optional[float] = None
    estimated_rul_max: Optional[float] = None
    model_version: str = "v1.0-heuristic-rf"
    features: Optional[Dict[str, Any]] = None
    explanation: Optional[List[Dict[str, Any]]] = None


class PredictionCreate(PredictionBase):
    pass


class PredictionOut(PredictionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class RULResponse(BaseModel):
    asset_id: str
    asset_name: str
    estimated_rul_min_years: float
    estimated_rul_max_years: float
    confidence: float
    basis: str
    features: Dict[str, Any] = {}
    explanation: List[Dict[str, Any]] = []


class AnomalyResponse(BaseModel):
    sensor_id: str
    is_anomaly: bool
    anomaly_score: float
    severity: str
    trigger_rule: Optional[str] = None
    details: Dict[str, Any] = {}
