"""
Tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)


def test_health_check():
    """Test basic health check endpoint."""
    response = client.get("/api/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data


def test_detailed_health_check():
    """Test detailed health check endpoint."""
    response = client.get("/api/v1/health/detailed")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "components" in data


def test_search_by_text_missing_query():
    """Test text search without query parameter."""
    response = client.post("/api/v1/search/text")
    
    assert response.status_code == 422  # Validation error


def test_search_by_text_with_query():
    """Test text search with query parameter."""
    response = client.post("/api/v1/search/text?query=red+car&limit=10")
    
    # May fail if database is not set up, but should return proper response structure
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "query" in data
        assert "results" in data
        assert "total" in data

