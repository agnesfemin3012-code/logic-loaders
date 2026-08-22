"""
Smart City Predictive Infrastructure - Prediction Endpoints
============================================================
FastAPI routes for project delay regression, risk classification,
and composite maintenance priority scoring.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from services.ml_service import ml_service
from services.recommendation_service import recommendation_engine

router = APIRouter(prefix="", tags=["Prediction Engine"])

class ProjectPredictRequest(BaseModel):
    project_type: str = Field(default="Road Construction", description="Type of infrastructure project")
    planned_duration: float = Field(default=60, ge=1, description="Planned project duration in days")
    current_progress: float = Field(default=55.0, ge=0, le=100, description="Current progress percentage (0-100)")
    traffic_volume: float = Field(default=900, ge=0, description="Traffic volume (vehicles per hour)")
    average_speed: float = Field(default=22.0, ge=1, description="Average vehicle speed (km/h)")
    rainfall: Optional[float] = Field(default=10.0, ge=0, description="Precipitation in mm (auto-enriched if omitted)")
    temperature: Optional[float] = Field(default=27.0, description="Ambient temperature in °C")
    humidity: Optional[float] = Field(default=80.0, ge=0, le=100, description="Relative humidity percentage")
    road_condition: int = Field(default=3, ge=1, le=5, description="Road condition score (1=Best, 5=Severely Degraded)")
    workers_available: int = Field(default=20, ge=1, description="Active workforce count")
    previous_delay: float = Field(default=5.0, ge=0, description="Historical delay in days")
    installed_year: Optional[int] = Field(default=2018, description="Year installed / constructed")

class ProjectPredictResponse(BaseModel):
    predicted_delay_days: int
    predicted_completion_days: int
    risk_level: str
    traffic_level: str
    weather_impact: str
    priority_analysis: Optional[Dict[str, Any]] = None
    recommended_actions: Optional[List[str]] = None
    alerts: Optional[List[Dict[str, str]]] = None

@router.post("/predict", response_model=ProjectPredictResponse)
def predict_infrastructure_delay(req: ProjectPredictRequest):
    """
    Main ML Prediction Endpoint.
    Calculates predicted delay, estimated completion time, risk classification,
    traffic congestion severity, and weather impact.
    """
    try:
        data = req.model_dump()
        prediction = ml_service.predict_project(data, enrich_weather=True)
        recommendations = recommendation_engine.generate_recommendations(data, prediction)
        
        return ProjectPredictResponse(
            predicted_delay_days=prediction["predicted_delay_days"],
            predicted_completion_days=prediction["predicted_completion_days"],
            risk_level=prediction["risk_level"],
            traffic_level=prediction["traffic_level"],
            weather_impact=prediction["weather_impact"],
            priority_analysis=prediction.get("priority_analysis"),
            recommended_actions=recommendations.get("recommended_actions"),
            alerts=recommendations.get("alerts")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.post("/predict/batch")
def batch_predict_infrastructure(projects: List[ProjectPredictRequest]):
    """
    Runs high-throughput batch predictions over multiple infrastructure projects.
    """
    results = []
    for p in projects:
        data = p.model_dump()
        pred = ml_service.predict_project(data, enrich_weather=True)
        rec = recommendation_engine.generate_recommendations(data, pred)
        results.append({
            "input": data,
            "prediction": pred,
            "recommendations": rec
        })
    return {"count": len(results), "predictions": results}

@router.get("/predict/demo")
def get_demo_prediction():
    """
    Convenience endpoint returning the official Hackathon Demo Scenario.
    """
    demo_input = {
        "project_type": "Road Construction",
        "planned_duration": 60,
        "current_progress": 55.0,
        "traffic_volume": 1120,
        "average_speed": 19.0,
        "rainfall": 8.0,
        "temperature": 27.0,
        "humidity": 80.0,
        "road_condition": 3,
        "workers_available": 18,
        "previous_delay": 5
    }
    pred = ml_service.predict_project(demo_input, enrich_weather=False)
    rec = recommendation_engine.generate_recommendations(demo_input, pred)
    return {
        "scenario": "Road Expansion – Zone A (Hackathon Benchmark)",
        "inputs": demo_input,
        "prediction": pred,
        "recommendations": rec
    }
