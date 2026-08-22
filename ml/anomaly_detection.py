from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from sklearn.ensemble import IsolationForest
from app.core.config import settings
from app.core.logging import logger


class AnomalyDetector:
    """
    Multi-strategy anomaly detector combining:
    1. Domain threshold rules (water pressure, vibration, temperature, rainfall)
    2. Statistical rolling Z-score & rate-of-change
    3. Isolation Forest for multivariate telemetry patterns
    """

    def __init__(self):
        # Domain thresholds for Pune infrastructure sensors
        self.thresholds = {
            "WATER_PRESSURE": {
                "min_normal": settings.PRESSURE_ANOMALY_DROP_PSI,  # 25 PSI
                "max_normal": settings.PRESSURE_ANOMALY_SPIKE_PSI,  # 80 PSI
                "max_rate_of_change": 15.0,  # PSI per reading interval
                "unit": "psi"
            },
            "FLOW": {
                "min_normal": 10.0,
                "max_normal": 500.0,
                "max_rate_of_change": 100.0,
                "unit": "L/min"
            },
            "VIBRATION": {
                "min_normal": 0.0,
                "max_normal": 4.5,
                "max_rate_of_change": 2.0,
                "unit": "mm/s"
            },
            "STRAIN": {
                "min_normal": -500.0,
                "max_normal": 1200.0,
                "max_rate_of_change": 300.0,
                "unit": "µε"
            },
            "WATER_LEVEL": {
                "min_normal": 0.5,
                "max_normal": 8.0,
                "max_rate_of_change": 2.0,
                "unit": "m"
            },
            "TEMPERATURE": {
                "min_normal": 10.0,
                "max_normal": 48.0,
                "max_rate_of_change": 8.0,
                "unit": "°C"
            }
        }

    def detect_single_reading(
        self,
        sensor_type: str,
        current_value: float,
        recent_values: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a single reading against rule-based, rate-of-change, and statistical anomaly criteria.
        """
        recent = recent_values or []
        sensor_type_key = sensor_type.upper()
        rules = self.thresholds.get(sensor_type_key, {})

        is_anomaly = False
        severity = "NORMAL"
        trigger = None
        score = 0.0  # 0.0 to 1.0

        # 1. Check direct threshold boundaries
        if rules:
            min_val = rules.get("min_normal")
            max_val = rules.get("max_normal")

            if max_val is not None and current_value > max_val:
                is_anomaly = True
                excess = (current_value - max_val) / max_val
                score = min(1.0, 0.6 + excess * 0.4)
                severity = "CRITICAL" if excess > 0.3 else "HIGH"
                trigger = f"High value {current_value:.1f} {rules.get('unit', '')} exceeds safety maximum {max_val}"
            elif min_val is not None and current_value < min_val:
                is_anomaly = True
                deficit = (min_val - current_value) / (min_val + 1e-5)
                score = min(1.0, 0.5 + deficit * 0.5)
                severity = "HIGH" if deficit > 0.4 else "MODERATE"
                trigger = f"Sudden drop to {current_value:.1f} {rules.get('unit', '')} below minimum threshold {min_val}"

        # 2. Check Rate of Change if previous reading is present
        if not is_anomaly and recent and rules.get("max_rate_of_change"):
            last_val = recent[-1]
            delta = abs(current_value - last_val)
            max_roc = rules["max_rate_of_change"]
            if delta > max_roc:
                is_anomaly = True
                score = min(1.0, 0.5 + (delta / max_roc) * 0.3)
                severity = "MODERATE"
                trigger = f"Rapid rate of change: delta of {delta:.1f} {rules.get('unit', '')} exceeded limit {max_roc}"

        # 3. Check Statistical Z-score if sufficient history (>= 5 readings)
        if len(recent) >= 5:
            arr = np.array(recent)
            mean = np.mean(arr)
            std = np.std(arr)
            if std > 1e-4:
                z_score = abs(current_value - mean) / std
                if z_score >= settings.ANOMALY_Z_SCORE_THRESHOLD:
                    is_anomaly = True
                    score = max(score, min(1.0, z_score / 6.0))
                    severity = "CRITICAL" if z_score > 4.5 else "HIGH"
                    trigger = trigger or f"Statistical Z-score {z_score:.2f} σ deviation from rolling mean {mean:.2f}"

        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": round(score, 3),
            "severity": severity,
            "trigger": trigger,
            "details": {
                "sensor_type": sensor_type,
                "current_value": current_value,
                "thresholds": rules,
                "history_points": len(recent),
            }
        }

    def train_and_predict_multivariate(self, data_matrix: np.ndarray) -> np.ndarray:
        """
        Fit an Isolation Forest on multivariate historical readings and return anomaly flags (-1 for anomaly, 1 for normal).
        """
        if data_matrix.shape[0] < 10:
            return np.ones(data_matrix.shape[0])
        
        clf = IsolationForest(contamination=0.05, random_state=42)
        preds = clf.fit_predict(data_matrix)
        return preds


anomaly_detector = AnomalyDetector()
