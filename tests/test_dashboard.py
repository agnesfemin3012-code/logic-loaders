import pytest
from fastapi.testclient import TestClient


def test_get_dashboard_summary(client: TestClient):
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()

    # Validate asset summary
    assert "assets" in data
    assert data["assets"]["total"] >= 5
    assert "by_type" in data["assets"]

    # Validate warnings summary
    assert "warnings" in data
    assert "total_active" in data["warnings"]

    # Validate projects summary
    assert "projects" in data
    assert data["projects"]["total"] >= 3

    # Validate predictions summary
    assert "predictions" in data

    # Validate situation
    assert "situation" in data
    assert data["situation"]["city"] == "Pune"
    assert data["situation"]["overall_risk"] in ("LOW", "MODERATE", "HIGH", "CRITICAL")
