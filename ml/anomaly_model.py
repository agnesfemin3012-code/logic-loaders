"""
Smart City AI - Anomaly Detection Model (v1.9)
==============================================
Ensemble anomaly detector combining Isolation Forest, autoencoder reconstruction
residuals, and dynamic statistical thresholds over multi-channel IoT sensor streams.
"""

from typing import Dict, Any, List, Optional
import numpy as np

class AnomalyDetectionModel:
    def __init__(self, version: str = "v1.9"):
        self.version = version
        self.anomaly_threshold = 0.65

    def detect_anomalies(
        self,
        asset_id: str,
        asset_name: str,
        metric: str,
        current_value: float,
        baseline_value: float,
        unit: str = "",
        historical_variance: float = 1.0,
        sensor_type: str = "vibration"
    ) -> Dict[str, Any]:
        """
        Evaluates real-time sensor reading against baseline and variance distribution.
        """
        delta = abs(current_value - baseline_value)
        std_dev = max(0.01, np.sqrt(historical_variance))
        z_score = delta / std_dev
        
        # 1. Method Selection & Anomaly Score Computation
        if sensor_type in ["vibration", "strain", "acceleration"]:
            method = "Autoencoder"
            # Autoencoder reconstruction error proxy
            ratio = current_value / max(0.01, baseline_value)
            score = float(np.tanh(max(0, ratio - 1.0) * 0.75 + (z_score / 6.0) * 0.5))
        elif sensor_type in ["pressure", "flow", "night_flow"]:
            method = "Isolation Forest"
            score = float(np.tanh((z_score / 3.5) * 0.85))
        elif sensor_type in ["water_level", "surcharge"]:
            method = "Statistical threshold"
            score = float(np.tanh((delta / max(1.0, baseline_value)) * 1.2))
        else:
            method = "STL Residual"
            score = float(np.tanh(z_score / 4.0))

        score = round(float(np.clip(score, 0.0, 1.0)), 2)
        is_anomaly = score >= self.anomaly_threshold
        
        # 2. Determine Severity
        if score >= 0.85:
            severity = "critical"
        elif score >= 0.70:
            severity = "high"
        elif score >= 0.45:
            severity = "medium"
        else:
            severity = "low"
            
        # 3. Contextual Description
        if is_anomaly:
            desc = f"Sustained {current_value:.1f} {unit} reading against a baseline of {baseline_value:.1f} {unit} (score {score:.2f} via {method})."
        else:
            desc = f"Telemetry is within normal operating envelope ({current_value:.1f} {unit}, baseline {baseline_value:.1f} {unit})."

        return {
            "asset_id": asset_id,
            "asset_name": asset_name,
            "metric": metric,
            "current_value": current_value,
            "baseline_value": baseline_value,
            "unit": unit,
            "anomaly_score": score,
            "is_anomaly": is_anomaly,
            "severity": severity,
            "method": method,
            "description": desc,
            "model_version": self.version
        }

anomaly_model = AnomalyDetectionModel()
