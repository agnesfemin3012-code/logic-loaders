from typing import Dict, Any, List, Tuple
from app.models.asset import CriticalityLevel, AssetType
from app.core.config import settings


# Expected asset lifespan in years by type
EXPECTED_LIFESPAN_YEARS = {
    AssetType.ROAD: 10.0,
    AssetType.BRIDGE: 60.0,
    AssetType.PIPELINE: 30.0,
    AssetType.WATER_NETWORK: 25.0,
    AssetType.DRAINAGE: 20.0,
    AssetType.SEWAGE: 25.0,
    AssetType.STREETLIGHT: 8.0,
    AssetType.METRO: 50.0,
    AssetType.FOOTPATH: 7.0,
    AssetType.FIRE_STATION: 40.0,
    AssetType.STP: 30.0,
    AssetType.OTHER: 15.0,
}

CRITICALITY_WEIGHTS = {
    CriticalityLevel.LOW: 1.0,
    CriticalityLevel.MEDIUM: 1.2,
    CriticalityLevel.HIGH: 1.5,
    CriticalityLevel.CRITICAL: 2.0,
}


class AssetHealthEngine:
    """
    Computes 0-100 Asset Health Score and 0-100 Risk Score with full explainability breakdown.
    Weights and thresholds are centralized and configurable.
    """

    def __init__(self):
        # Risk factor weights
        self.risk_weights = {
            "condition": 0.30,
            "sensor_anomalies": 0.25,
            "criticality": 0.20,
            "failure_history": 0.15,
            "environmental": 0.10,
        }

    def compute_health_score(
        self,
        asset_type: AssetType,
        condition: str,
        age_years: float,
        recent_anomalies_count: int = 0,
        unresolved_warnings_count: int = 0,
        days_since_last_maintenance: float = 60.0
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calculate health score (0-100) and list of contributing factors.
        """
        # 1. Base score from inspected physical condition
        cond_map = {
            "EXCELLENT": 100.0,
            "GOOD": 88.0,
            "FAIR": 68.0,
            "POOR": 42.0,
            "CRITICAL": 15.0,
        }
        base_score = cond_map.get(condition.upper(), 75.0)
        factors = []

        factors.append({
            "factor": "Physical Condition",
            "impact": "POSITIVE" if base_score >= 80 else ("NEUTRAL" if base_score >= 60 else "NEGATIVE"),
            "description": f"Visual inspection status: '{condition}' yields base score {base_score:.0f}/100."
        })

        # 2. Age Degradation Penalty
        lifespan = EXPECTED_LIFESPAN_YEARS.get(asset_type, 20.0)
        age_ratio = min(1.5, age_years / lifespan)
        age_penalty = 0.0
        if age_ratio > 0.5:
            age_penalty = (age_ratio - 0.5) * 30.0  # max ~30 points penalty for old assets
            factors.append({
                "factor": "Asset Age & Lifespan",
                "impact": "HIGH" if age_penalty > 15 else "MEDIUM",
                "description": f"Asset is {age_years:.1f} years old ({age_ratio*100:.0f}% of {lifespan:.0f}y expected lifespan)."
            })

        # 3. Sensor Anomaly Penalty
        anomaly_penalty = min(35.0, recent_anomalies_count * 7.0)
        if recent_anomalies_count > 0:
            factors.append({
                "factor": "Sensor Anomaly Frequency",
                "impact": "CRITICAL" if anomaly_penalty > 20 else "HIGH",
                "description": f"{recent_anomalies_count} telemetry anomalies recorded in recent operating window."
            })

        # 4. Warning & Maintenance Status
        warning_penalty = min(20.0, unresolved_warnings_count * 5.0)
        maintenance_penalty = 0.0
        if days_since_last_maintenance > 180:
            maintenance_penalty = min(15.0, (days_since_last_maintenance - 180) / 30.0 * 2.5)
            factors.append({
                "factor": "Maintenance Overdue",
                "impact": "MEDIUM",
                "description": f"Last preventive inspection was {days_since_last_maintenance:.0f} days ago."
            })

        health = max(0.0, min(100.0, base_score - age_penalty - anomaly_penalty - warning_penalty - maintenance_penalty))
        return round(health, 1), factors

    def compute_risk_score(
        self,
        health_score: float,
        criticality: CriticalityLevel,
        recent_anomalies_count: int = 0,
        historical_failures_count: int = 0,
        weather_risk_factor: float = 0.0,
        active_anomaly_score: float = 0.0
    ) -> Tuple[float, str, List[Dict[str, Any]]]:
        """
        Calculate composite risk score (0-100) and categorical risk level (LOW, MODERATE, HIGH, CRITICAL).
        """
        # Component 1: Inverse health (0-100)
        cond_risk = (100.0 - health_score)

        # Component 2: Sensor Anomaly Risk (0-100)
        anomaly_risk = min(100.0, max(recent_anomalies_count * 25.0, active_anomaly_score * 100.0))

        # Component 3: Criticality Multiplier normalized (0-100)
        crit_map = {
            CriticalityLevel.LOW: 25.0,
            CriticalityLevel.MEDIUM: 50.0,
            CriticalityLevel.HIGH: 80.0,
            CriticalityLevel.CRITICAL: 100.0,
        }
        criticality_risk = crit_map.get(criticality, 50.0)

        # Component 4: Historical Failure Risk (0-100)
        failure_risk = min(100.0, historical_failures_count * 25.0)

        # Component 5: Environmental Risk (0-100)
        env_risk = weather_risk_factor * 100.0

        # Weighted calculation
        total_risk = (
            self.risk_weights["condition"] * cond_risk +
            self.risk_weights["sensor_anomalies"] * anomaly_risk +
            self.risk_weights["criticality"] * criticality_risk +
            self.risk_weights["failure_history"] * failure_risk +
            self.risk_weights["environmental"] * env_risk
        )
        total_risk = max(0.0, min(100.0, total_risk))

        # Categorization
        if total_risk >= settings.RISK_THRESHOLD_CRITICAL:
            category = "CRITICAL"
        elif total_risk >= settings.RISK_THRESHOLD_HIGH:
            category = "HIGH"
        elif total_risk >= settings.RISK_THRESHOLD_MODERATE:
            category = "MODERATE"
        else:
            category = "LOW"

        # Risk Factors
        factors = []
        if cond_risk > 40:
            factors.append({"factor": "Degraded Infrastructure Condition", "impact": "HIGH" if cond_risk > 60 else "MEDIUM"})
        if anomaly_risk > 30:
            factors.append({"factor": "Sensor Telemetry Anomalies", "impact": "CRITICAL" if anomaly_risk > 60 else "HIGH"})
        if criticality in (CriticalityLevel.HIGH, CriticalityLevel.CRITICAL):
            factors.append({"factor": f"High Asset Criticality ({criticality.value})", "impact": "HIGH"})
        if failure_risk > 30:
            factors.append({"factor": "Past Failure Frequency", "impact": "MEDIUM"})
        if env_risk > 40:
            factors.append({"factor": "Monsoon / Extreme Weather Vulnerability", "impact": "HIGH"})

        return round(total_risk, 1), category, factors


asset_health_engine = AssetHealthEngine()
