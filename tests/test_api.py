"""
Basic API tests for the Slide Generator
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Slide Generator API is running"}

def test_create_presentation():
    """Test creating a new presentation"""
    presentation_data = {
        "topic": "Test Topic",
        "num_slides": 3,
        "custom_content": "Test custom content"
    }
    
    response = client.post("/api/v1/presentations", json=presentation_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["topic"] == "Test Topic"
    assert data["num_slides"] == 3
    assert data["custom_content"] == "Test custom content"
    assert "id" in data
    assert len(data["slides"]) == 3

def test_get_presentation():
    """Test retrieving a presentation"""
    # First create a presentation
    presentation_data = {
        "topic": "Get Test Topic",
        "num_slides": 2
    }
    
    create_response = client.post("/api/v1/presentations", json=presentation_data)
    assert create_response.status_code == 200
    
    presentation_id = create_response.json()["id"]
    
    # Then retrieve it
    get_response = client.get(f"/api/v1/presentations/{presentation_id}")
    assert get_response.status_code == 200
    
    data = get_response.json()
    assert data["id"] == presentation_id
    assert data["topic"] == "Get Test Topic"

def test_get_nonexistent_presentation():
    """Test retrieving a presentation that doesn't exist"""
    response = client.get("/api/v1/presentations/nonexistent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Presentation not found"

def test_configure_presentation():
    """Test configuring a presentation"""
    # First create a presentation
    presentation_data = {
        "topic": "Configure Test Topic",
        "num_slides": 2
    }
    
    create_response = client.post("/api/v1/presentations", json=presentation_data)
    assert create_response.status_code == 200
    
    presentation_id = create_response.json()["id"]
    
    # Then configure it
    config_data = {
        "theme": "minimal",
        "font": "Times New Roman",
        "colors": {
            "primary": "#FF0000",
            "secondary": "#00FF00",
            "background": "#FFFFFF",
            "text": "#000000"
        }
    }
    
    config_response = client.post(f"/api/v1/presentations/{presentation_id}/configure", json=config_data)
    assert config_response.status_code == 200
    
    data = config_response.json()
    assert data["theme"] == "minimal"
    assert data["font"] == "Times New Roman"
    assert data["colors"]["primary"] == "#FF0000" 