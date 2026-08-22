import pytest
from app.ml.anomaly_detection import anomaly_detector
from app.ml.health_score import asset_health_engine
from app.ml.failure_prediction import failure_predictor
from app.ml.rul_prediction import rul_predictor
from app.models.asset import AssetType, CriticalityLevel


def test_anomaly_detection_rules():
    # Normal pressure
    norm_res = anomaly_detector.detect_single_reading("WATER_PRESSURE", 54.0, [53.0, 55.0, 54.2])
    assert norm_res["is_anomaly"] is False

    # Pressure spike anomaly > 80 psi
    spike_res = anomaly_detector.detect_single_reading("WATER_PRESSURE", 88.0, [53.0, 55.0, 54.2])
    assert spike_res["is_anomaly"] is True
    assert spike_res["severity"] in ("HIGH", "CRITICAL")

    # Pressure drop anomaly < 25 psi
    drop_res = anomaly_detector.detect_single_reading("WATER_PRESSURE", 18.0, [53.0, 55.0, 54.2])
    assert drop_res["is_anomaly"] is True


def test_health_and_risk_scoring():
    # Good asset
    health, factors = asset_health_engine.compute_health_score(AssetType.PIPELINE, "Good", age_years=4.0)
    assert health >= 75.0

    risk, cat, _ = asset_health_engine.compute_risk_score(health, CriticalityLevel.MEDIUM)
    assert cat in ("LOW", "MODERATE")

    # Degraded asset with anomalies
    health_deg, _ = asset_health_engine.compute_health_score(
        AssetType.PIPELINE, "Poor", age_years=25.0, recent_anomalies_count=4
    )
    assert health_deg < 50.0

    risk_deg, cat_deg, _ = asset_health_engine.compute_risk_score(
        health_deg, CriticalityLevel.CRITICAL, recent_anomalies_count=4
    )
    assert risk_deg >= 65.0
    assert cat_deg in ("HIGH", "CRITICAL")


def test_failure_and_rul_prediction():
    fail_res = failure_predictor.predict(
        asset_type=AssetType.PIPELINE,
        health_score=45.0,
        risk_score=78.0,
        age_years=22.0,
        anomaly_count=3
    )
    assert fail_res["probability"] > 0.60
    assert fail_res["predicted_failure_window"] in ("Within 7 days", "Within 14 to 30 days")
    assert len(fail_res["explanation"]) > 0

    rul_res = rul_predictor.estimate_rul(
        asset_type=AssetType.PIPELINE,
        age_years=22.0,
        health_score=45.0,
        risk_score=78.0,
        anomaly_frequency=3
    )
    assert rul_res["estimated_rul_min_years"] < rul_res["estimated_rul_max_years"]
    assert rul_res["confidence"] > 0.5
