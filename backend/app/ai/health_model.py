"""
Smart City AI - Infrastructure Health Model (v4.2)
===================================================
Calculates comprehensive infrastructure health scores (0–100)
based on asset age, material degradation, inspection records,
active sensor telemetry, and historical maintenance interventions.
"""

from typing import Dict, Any, List, Optional
import numpy as np

class InfrastructureHealthModel:
    def __init__(self, version: str = "v4.2"):
        self.version = version
        self.weights = {
            "sensor_telemetry": 0.35,
            "physical_inspection": 0.25,
            "age_depreciation": 0.20,
            "maintenance_recency": 0.10,
            "environmental_load": 0.10
        }

    def calculate_health_score(
        self,
        asset_id: str,
        asset_kind: str,
        installed_year: int,
        inspection_score: float = 80.0, # 0 to 100
        sensor_anomalies_count: int = 0,
        vibration_rms: Optional[float] = None,
        pressure_deviation: Optional[float] = None,
        last_maintenance_days_ago: int = 45,
        environmental_severity: float = 1.0 # 1.0 (normal) to 2.0 (severe monsoon)
    ) -> Dict[str, Any]:
        """
        Computes composite health score (0-100), condition state, and breakdown.
        """
        current_year = 2026
        age = max(0, current_year - installed_year)
        
        # 1. Age Factor (Design life assumed 30-50 years depending on asset)
        design_life = 50.0 if asset_kind in ["bridge", "flyover", "stp"] else 30.0
        age_health = max(10.0, 100.0 - (age / design_life) * 80.0)
        
        # 2. Sensor Telemetry Score
        telemetry_penalty = sensor_anomalies_count * 15.0
        if vibration_rms is not None and vibration_rms > 2.5:
            telemetry_penalty += min(40.0, (vibration_rms - 2.5) * 18.0)
        if pressure_deviation is not None and abs(pressure_deviation) > 1.0:
            telemetry_penalty += min(35.0, abs(pressure_deviation) * 15.0)
            
        telemetry_score = max(5.0, 100.0 - telemetry_penalty)
        
        # 3. Physical Inspection Score
        inspection_health = float(np.clip(inspection_score, 0.0, 100.0))
        
        # 4. Maintenance Recency Score (Decays if untreated > 90 days)
        maintenance_health = max(20.0, 100.0 - (last_maintenance_days_ago / 180.0) * 60.0)
        
        # 5. Environmental Load Score
        env_health = max(20.0, 100.0 - (environmental_severity - 1.0) * 50.0)
        
        # Weighted aggregate
        composite_score = (
            telemetry_score * self.weights["sensor_telemetry"] +
            inspection_health * self.weights["physical_inspection"] +
            age_health * self.weights["age_depreciation"] +
            maintenance_health * self.weights["maintenance_recency"] +
            env_health * self.weights["environmental_load"]
        )
        
        composite_score = round(float(np.clip(composite_score, 0.0, 100.0)), 1)
        
        if composite_score >= 85:
            status = "Excellent"
            level = "low"
        elif composite_score >= 70:
            status = "Good"
            level = "low"
        elif composite_score >= 50:
            status = "Fair"
            level = "medium"
        elif composite_score >= 30:
            status = "Poor"
            level = "high"
        else:
            status = "Critical"
            level = "critical"
            
        return {
            "asset_id": asset_id,
            "asset_kind": asset_kind,
            "health_score": composite_score,
            "status": status,
            "risk_level": level,
            "model_version": self.version,
            "sub_scores": {
                "sensor_telemetry": round(telemetry_score, 1),
                "physical_inspection": round(inspection_health, 1),
                "age_depreciation": round(age_health, 1),
                "maintenance_recency": round(maintenance_health, 1),
                "environmental_load": round(env_health, 1)
            },
            "age_years": age,
            "recommendation": (
                "Routine monitoring" if composite_score >= 70
                else "Schedule preventive inspection within 14 days" if composite_score >= 50
                else "Immediate engineering verification and maintenance intervention required"
            )
        }

health_model = InfrastructureHealthModel()
