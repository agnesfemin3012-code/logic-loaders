import pytest
from fastapi.testclient import TestClient


def test_list_projects(client: TestClient):
    response = client.get("/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    proj_ids = [p["project_id"] for p in data]
    assert "PUN-METRO-L3" in proj_ids


def test_get_project_with_officer_attribution(client: TestClient):
    response = client.get("/api/projects/PUN-METRO-L3")
    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == "PUN-METRO-L3"
    assert data["name"] == "Pune Metro Line 3 (Hinjawadi to Shivajinagar Elevated Corridor)"
    assert data["officer"] is not None
    assert data["officer"]["employee_id"] == "PMRDA-ENG-4021"
    assert data["officer"]["designation"] == "Executive Engineer (Metro Infrastructure)"
    assert data["officer"]["public_contact"] is not None


def test_get_nearby_projects(client: TestClient):
    # Hinjawadi / Wakad corridor
    response = client.get("/api/projects/nearby?lat=18.5987&lng=73.7686&radius=3000")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    found_ids = [p["project_id"] for p in data]
    assert "PUN-ROAD-WKD" in found_ids or "PUN-METRO-L3" in found_ids
