from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class WeatherResponse(BaseModel):
    location: str = "Pune"
    temperature: float
    rainfall: float  # mm/hr or past 24h
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    condition: str
    risk: str  # LOW, MODERATE, HIGH, SEVERE
    alerts: List[str] = []
    timestamp: datetime
    source: str = "OpenMeteo / IMD Integration"
