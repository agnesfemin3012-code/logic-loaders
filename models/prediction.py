import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Enum, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class PredictionType(str, enum.Enum):
    FAILURE = "FAILURE"
    ANOMALY = "ANOMALY"
    HEALTH = "HEALTH"
    RUL = "RUL"


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("infrastructure_assets.id", ondelete="CASCADE"), nullable=False, index=True)
    prediction_type = Column(Enum(PredictionType), nullable=False, index=True)
    
    probability = Column(Float, nullable=True)  # e.g., 0.82 for 82% failure probability
    confidence = Column(Float, default=0.75, nullable=False)  # 0.0 to 1.0
    
    predicted_failure_window = Column(String(100), nullable=True)  # e.g., "Within 14 days"
    estimated_rul_min = Column(Float, nullable=True)  # in years, e.g., 1.5
    estimated_rul_max = Column(Float, nullable=True)  # in years, e.g., 3.0
    
    model_version = Column(String(50), default="v1.0-heuristic-rf", nullable=False)
    features = Column(JSON, nullable=True)  # feature dictionary used for inference
    explanation = Column(JSON, nullable=True)  # factor breakdown e.g. [{"factor": "Pressure Spikes", "impact": "HIGH"}]

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    asset = relationship("InfrastructureAsset", back_populates="predictions")

    __table_args__ = (
        Index("idx_prediction_asset_type", "asset_id", "prediction_type"),
    )
