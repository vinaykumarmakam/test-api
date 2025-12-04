"""Test suite for data product API"""
import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()
    assert "version" in response.json()

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_readiness_check():
    """Test readiness probe"""
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"

def test_process_data():
    """Test data processing endpoint"""
    payload = {
        "data": {"test": "value"},
        "priority": "high"
    }
    response = client.post("/api/v1/process", json=payload)
    assert response.status_code == 200
    assert "job_id" in response.json()
    assert response.json()["status"] == "queued"

def test_get_job_status():
    """Test job status endpoint"""
    job_id = "test_job_123"
    response = client.get(f"/api/v1/job/{job_id}")
    assert response.status_code == 200
    assert response.json()["job_id"] == job_id
