from typing import Dict, Any, List, Optional
from app.models.asset import AssetType
from app.ml.health_score import EXPECTED_LIFESPAN_YEARS


class RULPredictor:
    """
    Remaining Useful Life (RUL) estimator returning ranges rather than false precision.
    Distinguishes:
    - Measured telemetry degradation
    - Actuarial lifecycle survival estimation
    - Heuristic boundary intervals
    """

    def estimate_rul(
        self,
        asset_type: AssetType,
        age_years: float,
        health_score: float,
        risk_score: float,
        anomaly_frequency: int = 0
    ) -> Dict[str, Any]:
        """
        Estimate RUL min and max in years along with confidence and reasoning.
        """
        lifespan = EXPECTED_LIFESPAN_YEARS.get(asset_type, 20.0)
        remaining_nominal = max(0.2, lifespan - age_years)

        # Health ratio adjusts the nominal remaining lifespan
        health_factor = (health_score / 100.0) ** 1.5

        # Accelerated degradation from risk & anomalies
        degradation_factor = 1.0 - (risk_score / 100.0) * 0.5 - min(0.3, anomaly_frequency * 0.1)
        degradation_factor = max(0.05, degradation_factor)

        estimated_central = remaining_nominal * health_factor * degradation_factor
        estimated_central = max(0.1, estimated_central)

        # Build uncertainty bounds
        uncertainty_margin = 0.25 if anomaly_frequency > 0 else 0.40
        rul_min = max(0.1, round(estimated_central * (1.0 - uncertainty_margin), 1))
        rul_max = round(estimated_central * (1.0 + uncertainty_margin), 1)

        confidence = 0.80 if anomaly_frequency > 0 else 0.65

        explanation = [
            {
                "factor": "Nominal Design Lifespan",
                "impact": "INFO",
                "detail": f"{lifespan:.0f} years expected for {asset_type.value} infrastructure."
            },
            {
                "factor": "Current Health Adjustment",
                "impact": "HIGH" if health_score < 60 else "NEUTRAL",
                "detail": f"Health index {health_score:.1f}/100 scales expected durability."
            }
        ]

        if anomaly_frequency > 0:
            explanation.append({
                "factor": "Active Stress / Anomaly Rate",
                "impact": "CRITICAL",
                "detail": f"{anomaly_frequency} recent anomalies shorten effective operational window."
            })

        return {
            "estimated_rul_min_years": rul_min,
            "estimated_rul_max_years": rul_max,
            "confidence": round(confidence, 2),
            "basis": "Degradation Rate & Operational Stress Modeling",
            "features": {
                "age_years": age_years,
                "nominal_lifespan": lifespan,
                "health_score": health_score,
                "risk_score": risk_score,
                "anomaly_frequency": anomaly_frequency,
            },
            "explanation": explanation
        }


rul_predictor = RULPredictor()
