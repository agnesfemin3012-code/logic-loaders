import enum
from datetime import datetime, timezone, date
from sqlalchemy import Column, Integer, String, Float, Text, Date, DateTime, Enum, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class AssetType(str, enum.Enum):
    ROAD = "ROAD"
    BRIDGE = "BRIDGE"
    PIPELINE = "PIPELINE"
    WATER_NETWORK = "WATER_NETWORK"
    DRAINAGE = "DRAINAGE"
    SEWAGE = "SEWAGE"
    STREETLIGHT = "STREETLIGHT"
    METRO = "METRO"
    FOOTPATH = "FOOTPATH"
    FIRE_STATION = "FIRE_STATION"
    STP = "STP"
    OTHER = "OTHER"


class CriticalityLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AssetStatus(str, enum.Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    UNDER_MAINTENANCE = "UNDER_MAINTENANCE"
    DECOMMISSIONED = "DECOMMISSIONED"


class InfrastructureAsset(Base):
    __tablename__ = "infrastructure_assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    asset_type = Column(Enum(AssetType), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Spatial coordinates
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    geometry_wkt = Column(Text, nullable=True)  # WKT representation e.g. POINT(73.8567 18.5204)

    installation_date = Column(Date, nullable=True)
    material = Column(String(100), nullable=True)
    age = Column(Float, default=0.0, nullable=False)  # in years
    
    criticality = Column(Enum(CriticalityLevel), default=CriticalityLevel.MEDIUM, nullable=False, index=True)
    condition = Column(String(100), default="Good", nullable=False)
    health_score = Column(Float, default=100.0, nullable=False, index=True)
    risk_score = Column(Float, default=0.0, nullable=False, index=True)
    status = Column(Enum(AssetStatus), default=AssetStatus.NORMAL, nullable=False, index=True)

    # Source attribution
    source = Column(String(150), default="Pune Municipal Corporation", nullable=True)
    source_url = Column(String(500), nullable=True)
    source_record_id = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    sensors = relationship("Sensor", back_populates="asset", cascade="all, delete-orphan")
    warnings = relationship("Warning", back_populates="asset", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="asset", cascade="all, delete-orphan")
    work_orders = relationship("WorkOrder", back_populates="asset", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_asset_lat_lng", "latitude", "longitude"),
        Index("idx_asset_risk_status", "risk_score", "status"),
    )
