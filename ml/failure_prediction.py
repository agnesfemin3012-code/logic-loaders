from typing import Dict, Any, List, Optional
import numpy as np
from app.models.asset import AssetType, CriticalityLevel


class FailurePredictor:
    """
    Predicts probability of asset failure within specific operational timeframes
    using engineering reliability curves and telemetry indicators.
    """

    def predict(
        self,
        asset_type: AssetType,
        health_score: float,
        risk_score: float,
        age_years: float,
        anomaly_count: int,
        material: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Estimate failure probability, confidence, predicted failure window, and feature explanation.
        """
        # Baseline logistic sigmoid transformation of risk score
        z = (risk_score - 50.0) / 12.0
        prob = 1.0 / (1.0 + np.exp(-z))
        prob = float(np.clip(prob, 0.02, 0.98))

        # Determine failure window based on failure probability and anomaly count
        if prob > 0.80 or (anomaly_count >= 3 and risk_score >= 75):
            window = "Within 7 days"
            urgency = "IMMEDIATE"
        elif prob > 0.60 or anomaly_count >= 2:
            window = "Within 14 to 30 days"
            urgency = "HIGH"
        elif prob > 0.35:
            window = "1 to 3 months"
            urgency = "MEDIUM"
        else:
            window = "6+ months / Routine Lifecycle"
            urgency = "LOW"

        # Confidence based on availability of sensor data
        confidence = 0.85 if anomaly_count > 0 else 0.68

        explanation = []
        if risk_score >= 60:
            explanation.append({
                "factor": "Elevated Composite Risk Score",
                "impact": "HIGH",
                "detail": f"Current risk index is {risk_score:.1f}/100."
            })
        if anomaly_count > 0:
            explanation.append({
                "factor": "Sensor Anomalies Detected",
                "impact": "CRITICAL" if anomaly_count >= 2 else "HIGH",
                "detail": f"{anomaly_count} active anomaly events recorded."
            })
        if health_score < 50:
            explanation.append({
                "factor": "Structural/Mechanical Degradation",
                "impact": "HIGH",
                "detail": f"Health score is at {health_score:.1f}/100."
            })

        features = {
            "health_score": health_score,
            "risk_score": risk_score,
            "age_years": age_years,
            "anomaly_count": anomaly_count,
            "asset_type": asset_type.value,
            "material": material or "Unknown",
        }

        return {
            "probability": round(prob, 3),
            "confidence": round(confidence, 2),
            "predicted_failure_window": window,
            "urgency": urgency,
            "model_version": "v1.0-reliability-heuristic-ml",
            "features": features,
            "explanation": explanation
        }


failure_predictor = FailurePredictor()
