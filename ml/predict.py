"""
Smart City Predictive Infrastructure Maintenance - Standalone Prediction Engine
================================================================================
Loads the serialized RandomForest models and generates delay, completion,
risk level, traffic severity, and weather impact predictions.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Union, List
import pandas as pd
import numpy as np
import joblib

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
DELAY_MODEL_PATH = MODELS_DIR / "smart_city_delay_model.pkl"
RISK_MODEL_PATH = MODELS_DIR / "smart_city_risk_model.pkl"

CATEGORICAL_FEATURES = ["project_type"]
NUMERICAL_FEATURES = [
    "planned_duration",
    "current_progress",
    "traffic_volume",
    "average_speed",
    "rainfall",
    "temperature",
    "humidity",
    "road_condition",
    "workers_available",
    "previous_delay",
    "traffic_congestion_index",
    "weather_severity_index",
    "labor_density",
    "progress_rate"
]

# Global cache for loaded models
_delay_model = None
_risk_model = None

def get_models():
    """
    Lazy-loads and caches ML models in memory.
    """
    global _delay_model, _risk_model
    if _delay_model is None:
        if not DELAY_MODEL_PATH.exists():
            # Try to train if models don't exist yet
            from train_model import train_models
            train_models()
        _delay_model = joblib.load(DELAY_MODEL_PATH)
    
    if _risk_model is None:
        if not RISK_MODEL_PATH.exists():
            from train_model import train_models
            train_models()
        _risk_model = joblib.load(RISK_MODEL_PATH)
        
    return _delay_model, _risk_model

def compute_traffic_level(traffic_volume: float, average_speed: float) -> str:
    """Classifies traffic congestion level."""
    if traffic_volume >= 1500 or average_speed <= 15:
        return "CRITICAL"
    elif traffic_volume >= 900 or average_speed <= 22:
        return "HIGH"
    elif traffic_volume >= 500 or average_speed <= 35:
        return "MODERATE"
    else:
        return "LOW"

def compute_weather_impact(rainfall: float, humidity: float) -> str:
    """Classifies weather severity impact on construction/road."""
    if rainfall >= 45 or (rainfall >= 25 and humidity >= 85):
        return "SEVERE"
    elif rainfall >= 15 or (rainfall >= 8 and humidity >= 80):
        return "MODERATE"
    elif rainfall > 0:
        return "LOW"
    else:
        return "NONE"

def predict_single(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes a single project parameters dictionary and returns full ML predictions.
    
    Expected keys in `data`:
    - project_type (str, default: 'Road Construction')
    - planned_duration (int/float, default: 60)
    - current_progress (float, default: 50.0)
    - traffic_volume (int/float, default: 800)
    - average_speed (float, default: 25.0)
    - rainfall (float, default: 5.0)
    - temperature (float, default: 28.0)
    - humidity (float, default: 70.0)
    - road_condition (int, 1-5, default: 3)
    - workers_available (int, default: 20)
    - previous_delay (int/float, default: 0)
    """
    delay_model, risk_model = get_models()
    
    # Normalize inputs with fallbacks
    project_type = str(data.get("project_type", "Road Construction"))
    planned_duration = float(data.get("planned_duration", 60))
    current_progress = float(data.get("current_progress", 50.0))
    traffic_volume = float(data.get("traffic_volume", 800))
    average_speed = max(1.0, float(data.get("average_speed", 25.0)))
    rainfall = max(0.0, float(data.get("rainfall", 0.0)))
    temperature = float(data.get("temperature", 28.0))
    humidity = min(100.0, max(0.0, float(data.get("humidity", 65.0))))
    road_condition = int(data.get("road_condition", 3))
    workers_available = int(data.get("workers_available", 20))
    previous_delay = float(data.get("previous_delay", 0.0))
    
    # Feature engineering
    traffic_congestion_index = traffic_volume / (average_speed + 1.0)
    weather_severity_index = rainfall * (humidity / 100.0)
    labor_density = workers_available / (planned_duration + 1.0)
    progress_rate = current_progress / (planned_duration + 1.0)
    
    input_df = pd.DataFrame([{
        "project_type": project_type,
        "planned_duration": planned_duration,
        "current_progress": current_progress,
        "traffic_volume": traffic_volume,
        "average_speed": average_speed,
        "rainfall": rainfall,
        "temperature": temperature,
        "humidity": humidity,
        "road_condition": road_condition,
        "workers_available": workers_available,
        "previous_delay": previous_delay,
        "traffic_congestion_index": traffic_congestion_index,
        "weather_severity_index": weather_severity_index,
        "labor_density": labor_density,
        "progress_rate": progress_rate
    }])
    
    X = input_df[CATEGORICAL_FEATURES + NUMERICAL_FEATURES]
    
    # Model inference
    raw_delay = float(delay_model.predict(X)[0])
    predicted_delay_days = max(0, int(round(raw_delay)))
    predicted_completion_days = int(round(planned_duration + predicted_delay_days))
    risk_level = str(risk_model.predict(X)[0])
    
    traffic_level = compute_traffic_level(traffic_volume, average_speed)
    weather_impact = compute_weather_impact(rainfall, humidity)
    
    return {
        "predicted_delay_days": predicted_delay_days,
        "predicted_completion_days": predicted_completion_days,
        "risk_level": risk_level,
        "traffic_level": traffic_level,
        "weather_impact": weather_impact,
        "input_summary": {
            "project_type": project_type,
            "planned_duration": planned_duration,
            "current_progress": current_progress,
            "traffic_volume": traffic_volume,
            "average_speed": average_speed,
            "rainfall": rainfall
        }
    }

def run_demo():
    """Runs the Hackathon Demo scenario."""
    demo_input = {
        "project_type": "Road Construction",
        "planned_duration": 60,
        "current_progress": 55,
        "traffic_volume": 1120,
        "average_speed": 19,
        "rainfall": 8,
        "temperature": 27,
        "humidity": 80,
        "road_condition": 3,
        "workers_available": 18,
        "previous_delay": 5
    }
    
    print("\n=======================================================")
    print(" Smart City AI - Demo Scenario ('Road Expansion Zone A') ")
    print("=======================================================")
    print("Input Parameters:")
    print(json.dumps(demo_input, indent=2))
    
    result = predict_single(demo_input)
    print("\nML Predictions & Impact Assessment:")
    print(json.dumps(result, indent=2))
    print("=======================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smart City Infrastructure Predictor")
    parser.add_argument("--demo", action="store_true", help="Run hackathon demo prediction")
    parser.add_argument("--json", type=str, help="JSON input string of parameters")
    
    args = parser.parse_args()
    
    if args.demo or len(sys.argv) == 1:
        run_demo()
    elif args.json:
        try:
            data = json.loads(args.json)
            out = predict_single(data)
            print(json.dumps(out, indent=2))
        except Exception as e:
            print(f"Error executing prediction: {e}", file=sys.stderr)
            sys.exit(1)
