from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict
from app.models.sensor import SensorType, DeviceType, SensorStatus


class SensorBase(BaseModel):
    sensor_id: str
    asset_id: Optional[int] = None
    sensor_type: SensorType
    device_type: DeviceType = DeviceType.OTHER
    unit: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    metadata_json: Optional[Dict[str, Any]] = None


class SensorCreate(SensorBase):
    pass


class SensorOut(SensorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: SensorStatus
    installed_at: datetime
    last_seen: datetime
    created_at: datetime
    updated_at: datetime


class ReadingCreate(BaseModel):
    sensor_id: str
    value: float
    unit: Optional[str] = None
    timestamp: Optional[datetime] = None
    quality: Optional[str] = "GOOD"
    metadata: Optional[Dict[str, Any]] = None


class ReadingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sensor_id: str
    timestamp: datetime
    value: float
    unit: str
    quality: str
    metadata_json: Optional[Dict[str, Any]] = None


class ReadingIngestResponse(BaseModel):
    status: str = "success"
    sensor_id: str
    reading_id: int
    value: float
    unit: str
    is_anomaly: bool = False
    anomaly_score: Optional[float] = None
    warning_generated: bool = False
    warning_id: Optional[int] = None
    asset_risk_score: Optional[float] = None
