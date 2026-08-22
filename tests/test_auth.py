import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["city"] == "Pune"


def test_user_registration(client: TestClient):
    payload = {
        "name": "Pooja Deshmukh",
        "email": "pooja.d@testpune.com",
        "password": "SecurePassword123",
        "role": "CITIZEN",
        "phone": "+91-9876543210"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "pooja.d@testpune.com"
    assert data["user"]["role"] == "CITIZEN"


def test_user_login(client: TestClient):
    payload = {
        "email": "admin@test.gov.in",
        "password": "admin123"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "ADMIN"


def test_invalid_login(client: TestClient):
    payload = {
        "email": "admin@test.gov.in",
        "password": "wrongpassword"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401


def test_get_me(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@test.gov.in"
