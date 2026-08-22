from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models.asset import AssetType, CriticalityLevel, AssetStatus


class AssetBase(BaseModel):
    asset_id: str = Field(..., max_length=100)
    name: str = Field(..., max_length=255)
    asset_type: AssetType
    description: Optional[str] = None
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    installation_date: Optional[date] = None
    material: Optional[str] = None
    age: float = 0.0
    criticality: CriticalityLevel = CriticalityLevel.MEDIUM
    condition: str = "Good"
    source: Optional[str] = "Pune Municipal Corporation"
    source_url: Optional[str] = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    condition: Optional[str] = None
    criticality: Optional[CriticalityLevel] = None
    health_score: Optional[float] = None
    risk_score: Optional[float] = None
    status: Optional[AssetStatus] = None


class AssetOut(AssetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    health_score: float
    risk_score: float
    status: AssetStatus
    created_at: datetime
    updated_at: datetime


class AssetHealthFactor(BaseModel):
    factor: str
    impact: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str


class AssetHealthOut(BaseModel):
    asset_id: str
    name: str
    asset_type: AssetType
    health_score: float
    risk_score: float
    status: AssetStatus
    condition: str
    age_years: float
    factors: List[AssetHealthFactor] = []


class AssetNearbyQuery(BaseModel):
    lat: float
    lng: float
    radius: float = Field(1000.0, description="Radius in meters")
    asset_type: Optional[AssetType] = None
    min_risk: Optional[float] = None
