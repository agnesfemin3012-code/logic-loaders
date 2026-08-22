import pytest
from fastapi.testclient import TestClient


def test_list_assets(client: TestClient):
    response = client.get("/api/assets")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    asset_ids = [a["asset_id"] for a in data]
    assert "PUN-PIPE-001" in asset_ids
    assert "PUN-RD-001" in asset_ids


def test_get_asset_by_id(client: TestClient):
    response = client.get("/api/assets/PUN-PIPE-001")
    assert response.status_code == 200
    data = response.json()
    assert data["asset_id"] == "PUN-PIPE-001"
    assert data["asset_type"] == "PIPELINE"
    assert "health_score" in data
    assert "risk_score" in data


def test_get_asset_health_breakdown(client: TestClient):
    response = client.get("/api/assets/PUN-PIPE-001/health")
    assert response.status_code == 200
    data = response.json()
    assert data["asset_id"] == "PUN-PIPE-001"
    assert len(data["factors"]) > 0


def test_get_nearby_assets(client: TestClient):
    # Parvati coordinates
    response = client.get("/api/assets/nearby?lat=18.4975&lng=73.8510&radius=1500")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    found_ids = [a["asset_id"] for a in data]
    assert "PUN-PIPE-001" in found_ids
