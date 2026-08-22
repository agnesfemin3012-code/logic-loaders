import pytest
from fastapi.testclient import TestClient


def test_commute_analysis_hinjawadi_to_pune_station(client: TestClient):
    payload = {
        "origin": "Hinjawadi",
        "destination": "Pune Station",
        "mode": "driving",
        "buffer_radius_meters": 1000.0
    }
    response = client.post("/api/commute/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Verify Route
    assert "route" in data
    assert data["route"]["distance_meters"] > 5000.0
    assert data["route"]["duration_seconds"] > 600.0

    # Verify Risk & Weather
    assert "risk" in data
    assert data["risk"]["level"] in ("LOW", "MODERATE", "HIGH", "CRITICAL")
    assert "weather" in data
    assert data["weather"]["location"] == "Pune"

    # Verify Projects on Route (e.g. Metro Line 3 or Wakad Road works)
    assert "projects" in data
    assert len(data["projects"]) >= 1

    # Verify Recommendations
    assert "recommendations" in data
    assert len(data["recommendations"]) >= 1
