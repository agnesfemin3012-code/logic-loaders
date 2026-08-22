import pytest
from fastapi.testclient import TestClient


def test_list_warnings(client: TestClient):
    response = client.get("/api/warnings")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_acknowledge_warning(client: TestClient, officer_token: str):
    # First generate a warning by posting anomaly
    sensor_res = client.post("/api/sensors/readings", json={
        "sensor_id": "WP-001",
        "value": 91.2,
        "unit": "psi"
    })
    assert sensor_res.status_code == 201
    w_id = sensor_res.json().get("warning_id")
    assert w_id is not None

    # Acknowledge warning
    headers = {"Authorization": f"Bearer {officer_token}"}
    ack_res = client.post(f"/api/warnings/{w_id}/acknowledge", json={"notes": "Field team dispatched."}, headers=headers)
    assert ack_res.status_code == 200
    ack_data = ack_res.json()
    assert ack_data["status"] == "ACKNOWLEDGED"
    assert ack_data["acknowledged_by"] is not None
    assert len(ack_data["precautions"]) > 0
