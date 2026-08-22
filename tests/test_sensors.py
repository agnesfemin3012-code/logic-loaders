import pytest
from fastapi.testclient import TestClient


def test_list_sensors(client: TestClient):
    response = client.get("/api/sensors")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 4
    sensor_ids = [s["sensor_id"] for s in data]
    assert "WP-001" in sensor_ids


def test_ingest_normal_reading(client: TestClient):
    payload = {
        "sensor_id": "WP-001",
        "value": 55.4,
        "unit": "psi",
        "quality": "GOOD"
    }
    response = client.post("/api/sensors/readings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["sensor_id"] == "WP-001"
    assert data["is_anomaly"] is False


def test_ingest_anomaly_pressure_spike_triggers_warning(client: TestClient):
    # Ingest abnormal pressure spike (88.5 PSI) on WP-001 attached to PUN-PIPE-001
    payload = {
        "sensor_id": "WP-001",
        "value": 88.5,
        "unit": "psi",
        "quality": "GOOD"
    }
    response = client.post("/api/sensors/readings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["sensor_id"] == "WP-001"
    assert data["is_anomaly"] is True
    assert data["anomaly_score"] > 0.5
    assert data["warning_generated"] is True
    assert data["warning_id"] is not None

    # Verify asset risk was recalculated and updated
    asset_res = client.get("/api/assets/PUN-PIPE-001")
    assert asset_res.status_code == 200
    asset_data = asset_res.json()
    assert asset_data["risk_score"] >= 45.0
