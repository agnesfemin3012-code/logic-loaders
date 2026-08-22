import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class WarningSeverity(str, enum.Enum):
    INFO = "INFO"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class WarningStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class Warning(Base):
    __tablename__ = "warnings"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("infrastructure_assets.id", ondelete="CASCADE"), nullable=True, index=True)
    project_id = Column(Integer, ForeignKey("government_projects.id", ondelete="SET NULL"), nullable=True, index=True)
    
    warning_type = Column(String(100), nullable=False, index=True)  # PRESSURE_ANOMALY, HIGH_RISK, FLOOD_ALERT
    severity = Column(Enum(WarningSeverity), default=WarningSeverity.MODERATE, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    risk_score = Column(Float, nullable=False)
    trigger = Column(String(255), nullable=False)  # e.g., "Pressure spike to 88.5 PSI exceeded threshold"
    recommended_action = Column(Text, nullable=True)

    status = Column(Enum(WarningStatus), default=WarningStatus.ACTIVE, nullable=False, index=True)
    acknowledged_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    asset = relationship("InfrastructureAsset", back_populates="warnings")
    project = relationship("GovernmentProject", back_populates="warnings")
    precautions = relationship("Precaution", back_populates="warning", cascade="all, delete-orphan")
    work_orders = relationship("WorkOrder", back_populates="warning")

    __table_args__ = (
        Index("idx_warning_severity_status", "severity", "status"),
    )
