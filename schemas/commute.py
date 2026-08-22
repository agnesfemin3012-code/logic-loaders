from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.weather import WeatherResponse
from app.schemas.asset import AssetOut
from app.schemas.project import ProjectOut
from app.schemas.warning import WarningOut


class CommuteAnalyzeRequest(BaseModel):
    origin: str = Field(..., json_schema_extra={"example": "Hinjawadi Phase 1, Pune"})
    destination: str = Field(..., json_schema_extra={"example": "Pune Railway Station"})
    mode: str = Field("driving", json_schema_extra={"example": "driving"})
    buffer_radius_meters: float = Field(500.0, ge=100.0, le=5000.0)


class RouteGeometry(BaseModel):
    summary: str
    distance_meters: float
    duration_seconds: float
    polyline: Optional[str] = None
    start_address: Optional[str] = None
    end_address: Optional[str] = None
    start_coords: Dict[str, float]
    end_coords: Dict[str, float]


class CommuteRiskLevel(BaseModel):
    level: str  # LOW, MODERATE, HIGH, CRITICAL
    score: float
    primary_concerns: List[str] = []


class CommuteAnalyzeResponse(BaseModel):
    route: RouteGeometry
    risk: CommuteRiskLevel
    weather: WeatherResponse
    infrastructure: List[AssetOut] = []
    projects: List[ProjectOut] = []
    warnings: List[WarningOut] = []
    recommendations: List[str] = []
    data_sources: List[str] = []
