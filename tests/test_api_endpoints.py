"""
Tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test the health check endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Slide Generator API is running"}

class TestAuthentication:
    """Test authentication middleware"""
    
    def test_health_check_no_auth_required(self, client):
        """Health check should not require authentication"""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_docs_no_auth_required(self, client):
        """Documentation should not require authentication"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_presentations_require_auth(self, client):
        """Presentation endpoints should require authentication"""
        response = client.get("/api/v1/presentations")
        assert response.status_code == 401
    
    @patch.dict('os.environ', {'API_KEYS': 'test-key-123'})
    def test_valid_api_key_bearer(self, client):
        """Test with valid Bearer token"""
        headers = {"Authorization": "Bearer test-key-123"}
        response = client.get("/api/v1/presentations", headers=headers)
        assert response.status_code != 401  # Should not be unauthorized
    
    @patch.dict('os.environ', {'API_KEYS': 'test-key-123'})
    def test_valid_api_key_header(self, client):
        """Test with valid X-API-Key header"""
        headers = {"X-API-Key": "test-key-123"}
        response = client.get("/api/v1/presentations", headers=headers)
        assert response.status_code != 401  # Should not be unauthorized
    
    @patch.dict('os.environ', {'API_KEYS': 'test-key-123'})
    def test_invalid_api_key(self, client):
        """Test with invalid API key"""
        headers = {"Authorization": "Bearer invalid-key"}
        response = client.get("/api/v1/presentations", headers=headers)
        assert response.status_code == 401

class TestPresentations:
    """Test presentation endpoints"""
    
    @patch.dict('os.environ', {'API_KEYS': 'test-key-123'})
    def test_create_presentation(self, client, sample_presentation_data):
        """Test creating a new presentation"""
        headers = {"Authorization": "Bearer test-key-123"}
        response = client.post("/api/v1/presentations", 
                             json=sample_presentation_data, 
                             headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["topic"] == sample_presentation_data["topic"]
        assert data["num_slides"] == sample_presentation_data["num_slides"]
        assert "id" in data
        assert len(data["slides"]) == sample_presentation_data["num_slides"]
    
    @patch.dict('os.environ', {'API_KEYS': 'test-key-123'})
    def test_create_presentation_with_aspect_ratio(self, client):
        """Test creating presentation with specific aspect ratio"""
        headers = {"Authorization": "Bearer test-key-123"}
        data = {
            "topic": "Aspect Ratio Test",
            "num_slides": 2,
            "aspect_ratio": "16:9"
        }
        response = client.post("/api/v1/presentations", json=data, headers=headers)
        assert response.status_code == 200
        
        result = response.json()
        assert result["aspect_ratio"] == "16:9"
    
    @patch.dict('os.environ', {'API_KEYS': 'test-key-123'})
    def test_create_presentation_custom_aspect_ratio(self, client):
        """Test creating presentation with custom aspect ratio"""
        headers = {"Authorization": "Bearer test-key-123"}
        data = {
            "topic": "Custom Aspect Ratio Test",
            "num_slides": 2,
            "aspect_ratio": "custom",
            "custom_width": 12.0,
            "custom_height": 8.0
        }
        response = client.post("/api/v1/presentations", json=data, headers=headers)
        assert response.status_code == 200
        
        result = response.json()
        assert result["aspect_ratio"] == "custom"
        assert result["custom_width"] == 12.0
        assert result["custom_height"] == 8.0
    
    @patch.dict('os.environ', {'API_KEYS': 'test-key-123'})
    def test_get_presentation(self, client, sample_presentation_data):
        """Test retrieving a presentation"""
        headers = {"Authorization": "Bearer test-key-123"}
        
        # First create a presentation
        create_response = client.post("/api/v1/presentations", 
                                    json=sample_presentation_data, 
                                    headers=headers)
        assert create_response.status_code == 200
        presentation_id = create_response.json()["id"]
        
        # Then retrieve it
        get_response = client.get(f"/api/v1/presentations/{presentation_id}", 
                                headers=headers)
        assert get_response.status_code == 200
        
        data = get_response.json()
        assert data["id"] == presentation_id
        assert data["topic"] == sample_presentation_data["topic"]
    
    @patch.dict('os.environ', {'API_KEYS': 'test-key-123'})
    def test_get_nonexistent_presentation(self, client):
        """Test retrieving a presentation that doesn't exist"""
        headers = {"Authorization": "Bearer test-key-123"}
        response = client.get("/api/v1/presentations/nonexistent-id", 
                            headers=headers)
        assert response.status_code == 404
    
    @patch.dict('os.environ', {'API_KEYS': 'test-key-123'})
    def test_list_presentations(self, client, sample_presentation_data):
        """Test listing presentations"""
        headers = {"Authorization": "Bearer test-key-123"}
        
        # Create a presentation first
        client.post("/api/v1/presentations", 
                   json=sample_presentation_data, 
                   headers=headers)
        
        # List presentations
        response = client.get("/api/v1/presentations", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    @patch.dict('os.environ', {'API_KEYS': 'test-key-123'})
    def test_configure_presentation(self, client, sample_presentation_data, sample_presentation_config):
        """Test configuring a presentation"""
        headers = {"Authorization": "Bearer test-key-123"}
        
        # Create a presentation
        create_response = client.post("/api/v1/presentations", 
                                    json=sample_presentation_data, 
                                    headers=headers)
        assert create_response.status_code == 200
        presentation_id = create_response.json()["id"]
        
        # Configure it
        config_response = client.post(f"/api/v1/presentations/{presentation_id}/configure", 
                                    json=sample_presentation_config, 
                                    headers=headers)
        assert config_response.status_code == 200
        
        data = config_response.json()
        assert data["theme"] == sample_presentation_config["theme"]
        assert data["font"] == sample_presentation_config["font"]
        assert data["colors"]["primary"] == sample_presentation_config["colors"]["primary"]
        assert data["aspect_ratio"] == sample_presentation_config["aspect_ratio"]
    
    @patch.dict('os.environ', {'API_KEYS': 'test-key-123'})
    def test_delete_presentation(self, client, sample_presentation_data):
        """Test deleting a presentation"""
        headers = {"Authorization": "Bearer test-key-123"}
        
        # Create a presentation
        create_response = client.post("/api/v1/presentations", 
                                    json=sample_presentation_data, 
                                    headers=headers)
        assert create_response.status_code == 200
        presentation_id = create_response.json()["id"]
        
        # Delete it
        delete_response = client.delete(f"/api/v1/presentations/{presentation_id}", 
                                      headers=headers)
        assert delete_response.status_code == 200
        assert delete_response.json()["message"] == "Presentation deleted successfully"
        
        # Verify it's gone
        get_response = client.get(f"/api/v1/presentations/{presentation_id}", 
                                headers=headers)
        assert get_response.status_code == 404

class TestAspectRatios:
    """Test aspect ratio endpoints"""
    
    @patch.dict('os.environ', {'API_KEYS': 'test-key-123'})
    def test_get_aspect_ratios(self, client):
        """Test getting available aspect ratios"""
        headers = {"Authorization": "Bearer test-key-123"}
        response = client.get("/api/v1/aspect-ratios", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "available_aspect_ratios" in data
        assert "custom_support" in data
        assert "custom_limits" in data
        
        # Check that expected aspect ratios are present
        ratios = data["available_aspect_ratios"]
        assert "16:9" in ratios
        assert "4:3" in ratios
        assert "A4" in ratios
        assert "A4_L" in ratios
        assert "1:1" in ratios
        
        # Check custom limits
        limits = data["custom_limits"]
        assert limits["min_width"] == 5.0
        assert limits["max_width"] == 20.0
        assert limits["min_height"] == 5.0
        assert limits["max_height"] == 20.0

class TestSystemEndpoints:
    """Test system management endpoints"""
    
    @patch.dict('os.environ', {'API_KEYS': 'test-key-123'})
    def test_cache_stats(self, client):
        """Test getting cache statistics"""
        headers = {"Authorization": "Bearer test-key-123"}
        response = client.get("/api/v1/cache/stats", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "presentation_cache" in data
        assert "slide_cache" in data
        assert "api_cache" in data
    
    @patch.dict('os.environ', {'API_KEYS': 'test-key-123'})
    def test_clear_cache(self, client):
        """Test clearing cache"""
        headers = {"Authorization": "Bearer test-key-123"}
        response = client.post("/api/v1/cache/clear", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "All caches cleared"
    
    @patch.dict('os.environ', {'API_KEYS': 'test-key-123'})
    def test_llm_status(self, client):
        """Test getting LLM status"""
        headers = {"Authorization": "Bearer test-key-123"}
        response = client.get("/api/v1/llm/status", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "llm_service" in data
        assert "is_openai" in data
        assert "is_dummy" in data
    
    @patch.dict('os.environ', {'API_KEYS': 'test-key-123'})
    def test_concurrency_stats(self, client):
        """Test getting concurrency statistics"""
        headers = {"Authorization": "Bearer test-key-123"}
        response = client.get("/api/v1/concurrency/stats", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "global_semaphore" in data
        assert "user_semaphores" in data
        assert "limits" in data

class TestValidation:
    """Test input validation"""
    
    @patch.dict('os.environ', {'API_KEYS': 'test-key-123'})
    def test_invalid_num_slides(self, client):
        """Test validation of number of slides"""
        headers = {"Authorization": "Bearer test-key-123"}
        
        # Test too few slides
        data = {"topic": "Test", "num_slides": 0}
        response = client.post("/api/v1/presentations", json=data, headers=headers)
        assert response.status_code == 422
        
        # Test too many slides
        data = {"topic": "Test", "num_slides": 21}
        response = client.post("/api/v1/presentations", json=data, headers=headers)
        assert response.status_code == 422
    
    @patch.dict('os.environ', {'API_KEYS': 'test-key-123'})
    def test_invalid_custom_dimensions(self, client):
        """Test validation of custom dimensions"""
        headers = {"Authorization": "Bearer test-key-123"}
        
        # Test invalid custom dimensions
        data = {
            "topic": "Test",
            "num_slides": 3,
            "aspect_ratio": "custom",
            "custom_width": 3.0,  # Too small
            "custom_height": 8.0
        }
        response = client.post("/api/v1/presentations", json=data, headers=headers)
        assert response.status_code == 422
        
        # Test missing custom dimensions
        data = {
            "topic": "Test",
            "num_slides": 3,
            "aspect_ratio": "custom"
            # Missing custom_width and custom_height
        }
        response = client.post("/api/v1/presentations", json=data, headers=headers)
        assert response.status_code == 422 