import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_plan_trip():
    payload = {
        "user_id": "user_test_123",
        "destination": "Switzerland",
        "duration_days": 5,
        "budget": 3000.0,
        "currency": "USD",
        "additional_notes": "Vegetarian meal preference"
    }
    response = client.post("/api/v1/travel/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["destination"] == "Switzerland"
    assert data["duration_days"] == 5
    assert len(data["itinerary"]) == 5
    assert len(data["flights"]) > 0
    assert len(data["hotels"]) > 0
    assert "session_id" in data
    assert "conversation_id" in data

def test_plan_trip_stream():
    payload = {
        "user_id": "user_test_123",
        "destination": "Paris",
        "duration_days": 3
    }
    response = client.post("/api/v1/travel/plan/stream", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
