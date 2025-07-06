"""
Tests for middleware components
"""
import pytest
import time
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.middleware.rate_limiter import RateLimiter
from app.middleware.auth import AuthMiddleware
from app.middleware.concurrency import ConcurrencyController

class TestRateLimiter:
    """Test rate limiting functionality"""
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization"""
        limiter = RateLimiter(requests_per_minute=30, requests_per_hour=500)
        assert limiter.requests_per_minute == 30
        assert limiter.requests_per_hour == 500
    
    def test_get_client_ip_forwarded_for(self):
        """Test client IP extraction with X-Forwarded-For"""
        limiter = RateLimiter()
        request = Mock()
        request.headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        request.client = None
        
        ip = limiter._get_client_ip(request)
        assert ip == "192.168.1.1"
    
    def test_get_client_ip_real_ip(self):
        """Test client IP extraction with X-Real-IP"""
        limiter = RateLimiter()
        request = Mock()
        request.headers = {"X-Real-IP": "192.168.1.2"}
        request.client = None
        
        ip = limiter._get_client_ip(request)
        assert ip == "192.168.1.2"
    
    def test_get_client_ip_direct(self):
        """Test client IP extraction from direct connection"""
        limiter = RateLimiter()
        request = Mock()
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.3"
        
        ip = limiter._get_client_ip(request)
        assert ip == "192.168.1.3"
    
    def test_get_client_ip_unknown(self):
        """Test client IP extraction fallback"""
        limiter = RateLimiter()
        request = Mock()
        request.headers = {}
        request.client = None
        
        ip = limiter._get_client_ip(request)
        assert ip == "unknown"
    
    def test_rate_limit_key_generation(self):
        """Test rate limit key generation"""
        limiter = RateLimiter()
        key = limiter._get_rate_limit_key("192.168.1.1", "minute")
        assert "rate_limit:192.168.1.1:minute:" in key
    
    def test_rate_limit_check(self):
        """Test rate limit checking"""
        limiter = RateLimiter(requests_per_minute=2, requests_per_hour=10)
        
        # Mock cache responses
        limiter.cache.get_api_response = Mock(side_effect=[
            {"count": 1},  # minute requests
            {"count": 5}   # hour requests
        ])
        
        result = limiter._check_rate_limit("192.168.1.1")
        assert result["minute_requests"] == 1
        assert result["hour_requests"] == 5
        assert not result["minute_exceeded"]
        assert not result["hour_exceeded"]
    
    def test_rate_limit_exceeded(self):
        """Test rate limit exceeded scenario"""
        limiter = RateLimiter(requests_per_minute=2, requests_per_hour=10)
        
        # Mock cache responses showing exceeded limits
        limiter.cache.get_api_response = Mock(side_effect=[
            {"count": 2},  # minute requests (at limit)
            {"count": 10}  # hour requests (at limit)
        ])
        
        result = limiter._check_rate_limit("192.168.1.1")
        assert result["minute_exceeded"]
        assert result["hour_exceeded"]

class TestAuthMiddleware:
    """Test authentication middleware"""
    
    def test_auth_middleware_initialization(self):
        """Test auth middleware initialization"""
        with patch.dict('os.environ', {'API_KEYS': 'key1,key2,key3'}):
            auth = AuthMiddleware()
            assert "key1" in auth.api_keys
            assert "key2" in auth.api_keys
            assert "key3" in auth.api_keys
    
    def test_auth_middleware_no_keys(self):
        """Test auth middleware with no API keys"""
        with patch.dict('os.environ', {}, clear=True):
            auth = AuthMiddleware()
            assert len(auth.api_keys) == 0
    
    def test_get_api_key_bearer(self):
        """Test API key extraction from Bearer token"""
        auth = AuthMiddleware()
        request = Mock()
        request.headers = {"Authorization": "Bearer test-key-123"}
        
        key = auth._get_api_key_from_header(request)
        assert key == "test-key-123"
    
    def test_get_api_key_header(self):
        """Test API key extraction from X-API-Key header"""
        auth = AuthMiddleware()
        request = Mock()
        request.headers = {"X-API-Key": "api-key-456"}
        
        key = auth._get_api_key_from_header(request)
        assert key == "api-key-456"
    
    def test_get_api_key_none(self):
        """Test API key extraction when no key present"""
        auth = AuthMiddleware()
        request = Mock()
        request.headers = {}
        
        key = auth._get_api_key_from_header(request)
        assert key is None
    
    def test_validate_api_key_valid(self):
        """Test API key validation with valid key"""
        with patch.dict('os.environ', {'API_KEYS': 'valid-key-1,valid-key-2'}):
            auth = AuthMiddleware()
            assert auth._validate_api_key("valid-key-1") is True
            assert auth._validate_api_key("valid-key-2") is True
    
    def test_validate_api_key_invalid(self):
        """Test API key validation with invalid key"""
        with patch.dict('os.environ', {'API_KEYS': 'valid-key-1,valid-key-2'}):
            auth = AuthMiddleware()
            assert auth._validate_api_key("invalid-key") is False
    
    def test_validate_api_key_no_keys_configured(self):
        """Test API key validation when no keys configured"""
        with patch.dict('os.environ', {}, clear=True):
            auth = AuthMiddleware()
            assert auth._validate_api_key("any-key") is True
    
    def test_should_skip_auth(self):
        """Test authentication skip logic"""
        auth = AuthMiddleware()
        assert auth._should_skip_auth("/") is True
        assert auth._should_skip_auth("/docs") is True
        assert auth._should_skip_auth("/openapi.json") is True
        assert auth._should_skip_auth("/api/v1/cache/stats") is True
        assert auth._should_skip_auth("/api/v1/llm/status") is True
        assert auth._should_skip_auth("/api/v1/presentations") is False
        assert auth._should_skip_auth("/docs/static/swagger-ui.css") is True
    
    def test_get_user_info(self):
        """Test user info extraction"""
        auth = AuthMiddleware()
        user_info = auth._get_user_info("test-api-key-12345")
        
        assert user_info["user_id"] == "user_test-a"
        assert user_info["api_key"] == "test-api-key-12345"
        assert "read" in user_info["permissions"]
        assert "write" in user_info["permissions"]

class TestConcurrencyController:
    """Test concurrency control functionality"""
    
    def test_concurrency_controller_initialization(self):
        """Test concurrency controller initialization"""
        controller = ConcurrencyController(max_concurrent_requests=50, max_concurrent_per_user=5)
        assert controller.max_concurrent_requests == 50
        assert controller.max_concurrent_per_user == 5
    
    def test_get_user_id_authenticated(self):
        """Test user ID extraction for authenticated user"""
        controller = ConcurrencyController()
        request = Mock()
        request.state.user = {"user_id": "user_123"}
        request.client = None
        
        user_id = controller._get_user_id(request)
        assert user_id == "user_123"
    
    def test_get_user_id_ip_fallback(self):
        """Test user ID extraction with IP fallback"""
        controller = ConcurrencyController()
        request = Mock()
        request.state = Mock()
        request.client = Mock()
        request.client.host = "192.168.1.1"
        
        user_id = controller._get_user_id(request)
        assert user_id == "ip_192.168.1.1"
    
    def test_should_apply_concurrency_control(self):
        """Test concurrency control application logic"""
        controller = ConcurrencyController()
        
        # Should apply control
        assert controller._should_apply_concurrency_control("/api/v1/presentations") is True
        assert controller._should_apply_concurrency_control("/api/v1/presentations/123/download") is True
        
        # Should not apply control
        assert controller._should_apply_concurrency_control("/api/v1/presentations/123") is False
        assert controller._should_apply_concurrency_control("/") is False
        assert controller._should_apply_concurrency_control("/docs") is False
    
    def test_get_user_semaphore(self):
        """Test user semaphore creation and retrieval"""
        controller = ConcurrencyController(max_concurrent_per_user=3)
        
        # Get semaphore for new user
        sem1 = controller._get_user_semaphore("user_1")
        assert sem1._value == 3
        
        # Get semaphore for same user (should be cached)
        sem2 = controller._get_user_semaphore("user_1")
        assert sem1 is sem2
        
        # Get semaphore for different user
        sem3 = controller._get_user_semaphore("user_2")
        assert sem3 is not sem1
        assert sem3._value == 3
    
    def test_concurrency_stats(self):
        """Test concurrency statistics"""
        controller = ConcurrencyController(max_concurrent_requests=10, max_concurrent_per_user=5)
        
        # Create a user semaphore
        controller._get_user_semaphore("user_1")
        
        stats = controller.get_concurrency_stats()
        
        assert "global_semaphore" in stats
        assert "user_semaphores" in stats
        assert "limits" in stats
        
        assert stats["limits"]["max_concurrent_requests"] == 10
        assert stats["limits"]["max_concurrent_per_user"] == 5
        assert "user_1" in stats["user_semaphores"]

class TestMiddlewareIntegration:
    """Test middleware integration with FastAPI"""
    
    @patch.dict('os.environ', {'API_KEYS': 'test-key-123'})
    def test_rate_limit_headers(self, client):
        """Test that rate limit headers are added to responses"""
        headers = {"Authorization": "Bearer test-key-123"}
        response = client.get("/api/v1/presentations", headers=headers)
        
        # Check for rate limit headers
        assert "X-RateLimit-Minute-Limit" in response.headers
        assert "X-RateLimit-Minute-Remaining" in response.headers
        assert "X-RateLimit-Hour-Limit" in response.headers
        assert "X-RateLimit-Hour-Remaining" in response.headers
    
    @patch.dict('os.environ', {'API_KEYS': 'test-key-123'})
    def test_concurrency_headers(self, client):
        """Test that concurrency headers are added to responses"""
        headers = {"Authorization": "Bearer test-key-123"}
        response = client.get("/api/v1/presentations", headers=headers)
        
        # Check for concurrency headers
        assert "X-Concurrency-User-ID" in response.headers
        assert "X-Concurrency-Global-Limit" in response.headers
        assert "X-Concurrency-User-Limit" in response.headers
    
    @patch.dict('os.environ', {'API_KEYS': 'test-key-123'})
    def test_auth_headers(self, client):
        """Test that auth headers are added to responses"""
        headers = {"Authorization": "Bearer test-key-123"}
        response = client.get("/api/v1/presentations", headers=headers)
        
        # Check for auth headers
        assert "X-User-ID" in response.headers
    
    def test_health_check_middleware_headers(self, client):
        """Test that middleware headers are present on health check"""
        response = client.get("/")
        
        # Health check should have middleware headers
        assert "X-RateLimit-Minute-Limit" in response.headers
        assert "X-RateLimit-Minute-Remaining" in response.headers
        assert "X-Concurrency-User-ID" in response.headers
        assert "X-Concurrency-Global-Limit" in response.headers

class TestMiddlewareErrorHandling:
    """Test middleware error handling"""
    
    def test_rate_limit_exceeded_response(self, client):
        """Test rate limit exceeded response"""
        # Make many requests quickly to trigger rate limit
        # Note: This is a basic test - in practice you'd need to mock the cache
        # to simulate rate limit exceeded scenarios
        pass
    
    def test_concurrency_exceeded_response(self, client):
        """Test concurrency exceeded response"""
        # Test would require mocking semaphores to simulate concurrency limits
        pass
    
    def test_auth_error_response(self, client):
        """Test authentication error response"""
        response = client.get("/api/v1/presentations")
        assert response.status_code == 401
        
        error_data = response.json()
        assert "error" in error_data
        assert "message" in error_data
        assert "Unauthorized" in error_data["error"] 