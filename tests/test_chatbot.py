import pytest
from fastapi.testclient import TestClient


def test_chatbot_commute_query(client: TestClient):
    payload = {
        "message": "I want to go from Hinjawadi to Pune Station. What should I know?"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "COMMUTE_QUERY"
    assert "response" in data
    assert len(data["response"]) > 50
    assert "context_used" in data
    assert "route" in data["context_used"]


def test_chatbot_project_query(client: TestClient):
    payload = {
        "message": "Tell me about the metro line 3 project and who is the officer in charge"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "PROJECT_QUERY"
    assert len(data["context_used"]["projects"]) > 0


def test_chatbot_weather_query(client: TestClient):
    payload = {
        "message": "What is the current weather and rain condition in Pune?"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "WEATHER_QUERY"
    assert "weather" in data["context_used"]
