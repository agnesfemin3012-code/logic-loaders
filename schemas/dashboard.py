from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.schemas.asset import AssetOut
from app.schemas.warning import WarningOut
from app.schemas.project import ProjectOut
from app.schemas.weather import WeatherResponse


class AssetCounts(BaseModel):
    total: int = 0
    healthy: int = 0
    at_risk: int = 0
    critical: int = 0
    by_type: Dict[str, int] = {}


class WarningCounts(BaseModel):
    critical: int = 0
    high: int = 0
    moderate: int = 0
    low: int = 0
    info: int = 0
    total_active: int = 0


class ProjectCounts(BaseModel):
    ongoing: int = 0
    delayed: int = 0
    planned: int = 0
    completed: int = 0
    total: int = 0


class PredictionCounts(BaseModel):
    next_7_days: int = 0
    next_30_days: int = 0
    high_probability_failures: int = 0


class SituationOverview(BaseModel):
    city: str = "Pune"
    overall_risk: str  # LOW, MODERATE, HIGH, CRITICAL
    alert_level: str
    active_incidents: int = 0
    high_risk_zones: List[str] = []


class DashboardSummaryResponse(BaseModel):
    assets: AssetCounts
    warnings: WarningCounts
    projects: ProjectCounts
    predictions: PredictionCounts
    situation: SituationOverview
    recent_critical_warnings: List[WarningOut] = []
    high_risk_assets: List[AssetOut] = []
    weather: Optional[WeatherResponse] = None
