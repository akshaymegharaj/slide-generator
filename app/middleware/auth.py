"""
Basic Authentication Middleware
Supports API key authentication
"""
import os
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.factory import service_factory

# Security scheme for API documentation
security = HTTPBearer(auto_error=False)

class AuthMiddleware:
    """Basic authentication middleware using API keys"""
    
    def __init__(self):
        self.cache = service_factory.get_cache_service()
        # Load API keys from environment (comma-separated)
        self.api_keys = self._load_api_keys()
    
    def _load_api_keys(self) -> set:
        """Load API keys from environment variables"""
        api_keys_str = os.getenv("API_KEYS", "")
        if api_keys_str:
            return set(key.strip() for key in api_keys_str.split(",") if key.strip())
        return set()
    
    def _get_api_key_from_header(self, request: Request) -> Optional[str]:
        """Extract API key from request headers"""
        # Check Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix
        
        # Check X-API-Key header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return api_key
        
        return None
    
    def _validate_api_key(self, api_key: str) -> bool:
        """Validate API key"""
        if not self.api_keys:
            # If no API keys configured, allow all requests
            return True
        
        return api_key in self.api_keys
    
    def _get_user_info(self, api_key: str) -> Dict[str, Any]:
        """Get user information from API key (basic implementation)"""
        # In a real implementation, you might look up user info in a database
        # For now, we'll use the API key as a simple identifier
        return {
            "user_id": f"user_{api_key[:8]}",  # Use first 8 chars of API key
            "api_key": api_key,
            "permissions": ["read", "write"]  # Basic permissions
        }
    
    async def __call__(self, request: Request, call_next):
        """Middleware function to authenticate requests"""
        # Skip authentication for certain endpoints
        if self._should_skip_auth(request.url.path):
            return await call_next(request)
        
        # Get API key from request
        api_key = self._get_api_key_from_header(request)
        
        if not api_key:
            return self._unauthorized_response("API key required")
        
        # Validate API key
        if not self._validate_api_key(api_key):
            return self._unauthorized_response("Invalid API key")
        
        # Get user info and add to request state
        user_info = self._get_user_info(api_key)
        request.state.user = user_info
        
        # Continue with the request
        response = await call_next(request)
        
        # Add user info to response headers for debugging
        response.headers["X-User-ID"] = user_info["user_id"]
        
        return response
    
    def _should_skip_auth(self, path: str) -> bool:
        """Check if authentication should be skipped for this path"""
        skip_paths = {
            "/",  # Health check
            "/docs",  # API documentation
            "/openapi.json",  # OpenAPI schema
            "/api/v1/cache/stats",  # Cache stats (for debugging)
            "/api/v1/llm/status",  # LLM status (for debugging)
        }
        return path in skip_paths or path.startswith("/docs/")
    
    def _unauthorized_response(self, message: str):
        """Return unauthorized response"""
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=401,
            content={
                "error": "Unauthorized",
                "message": message
            },
            headers={"WWW-Authenticate": "Bearer"}
        )

# Global auth middleware instance
auth_middleware = AuthMiddleware()

# Dependency for getting current user
async def get_current_user(request: Request) -> Dict[str, Any]:
    """Dependency to get current authenticated user"""
    if not hasattr(request.state, 'user'):
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    return request.state.user

# Dependency for optional authentication
async def get_optional_user(request: Request) -> Optional[Dict[str, Any]]:
    """Dependency to get current user if authenticated, None otherwise"""
    return getattr(request.state, 'user', None) 