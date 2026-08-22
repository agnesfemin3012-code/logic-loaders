"""
Smart City AI - Failure Prediction Model (v3.1)
================================================
Calculates empirical failure probabilities, forecasting windows, confidence
levels, and primary drivers using multi-parameter risk and degradation modeling.
"""

from typing import Dict, Any, List, Optional
import numpy as np

class FailurePredictionModel:
    def __init__(self, version: str = "v3.1"):
        self.version = version

    def predict_failure(
        self,
        asset_id: str,
        asset_name: str,
        asset_kind: str,
        health_score: float,
        anomaly_score: float = 0.0,
        age_years: int = 15,
        monsoon_rainfall_mm: float = 0.0,
        days_since_last_inspection: int = 60,
        primary_sensor_deviation_pct: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculates failure probability (0-100%), forecast horizon window,
        confidence interval, and identified primary driving signal.
        """
        # Feature weighting for failure prediction
        w_anomaly = 0.40
        w_health = 0.25
        w_age = 0.15
        w_env = 0.12
        w_inspection = 0.08
        
        # Component probability contributions (0 to 100)
        anomaly_term = anomaly_score * 100.0
        health_term = (100.0 - health_score)
        age_term = min(100.0, (age_years / 40.0) * 100.0)
        env_term = min(100.0, (monsoon_rainfall_mm / 60.0) * 100.0)
        inspection_term = min(100.0, (days_since_last_inspection / 180.0) * 100.0)
        
        raw_prob = (
            anomaly_term * w_anomaly +
            health_term * w_health +
            age_term * w_age +
            env_term * w_env +
            inspection_term * w_inspection
        )
        
        prob = int(np.clip(round(raw_prob), 5, 98))
        
        # 1. Determine Forecast Window
        if prob >= 80:
            window = "21 days" if asset_kind in ["bridge", "flyover"] else "24 hours" if asset_kind in ["drain", "sewage"] else "7 days"
        elif prob >= 60:
            window = "6 weeks"
        elif prob >= 35:
            window = "90 days"
        else:
            window = "180 days"
            
        # 2. Determine Primary Driver
        drivers = [
            (anomaly_term * w_anomaly, "Telemetry vibration/pressure deviation trend"),
            (health_term * w_health, "Degraded structural health index"),
            (age_term * w_age, f"Asset operating age ({age_years} years)"),
            (env_term * w_env, f"Heavy rainfall exposure ({monsoon_rainfall_mm:.1f} mm)"),
            (inspection_term * w_inspection, f"Deferred inspection ({days_since_last_inspection} days ago)")
        ]
        drivers.sort(key=lambda x: x[0], reverse=True)
        primary_driver = drivers[0][1]
        
        # 3. Model Confidence Estimation
        confidence = int(np.clip(70 + (anomaly_score * 15.0) + (10 if days_since_last_inspection < 90 else -5), 60, 95))
        
        return {
            "asset_id": asset_id,
            "asset_name": asset_name,
            "failure_probability": prob,
            "window": window,
            "confidence": confidence,
            "driver": primary_driver,
            "model": f"Failure Prediction {self.version}",
            "details": {
                "health_score": health_score,
                "anomaly_score": anomaly_score,
                "age_years": age_years,
                "rainfall_mm": monsoon_rainfall_mm
            }
        }

failure_model = FailurePredictionModel()
