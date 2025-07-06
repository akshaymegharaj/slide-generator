"""
Concurrency Control Middleware
Handles multiple simultaneous requests efficiently
"""
import asyncio
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.services.factory import service_factory

class ConcurrencyController:
    """Middleware for handling concurrent requests efficiently"""
    
    def __init__(self, max_concurrent_requests: int = 100, max_concurrent_per_user: int = 10):
        self.max_concurrent_requests = max_concurrent_requests
        self.max_concurrent_per_user = max_concurrent_per_user
        self.cache = service_factory.get_cache_service()
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.user_semaphores: Dict[str, asyncio.Semaphore] = {}
    
    def _get_user_id(self, request: Request) -> str:
        """Get user ID from request state or IP address"""
        if hasattr(request.state, 'user') and request.state.user:
            return request.state.user.get("user_id", "anonymous")
        
        # Fallback to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip_{client_ip}"
    
    def _get_user_semaphore(self, user_id: str) -> asyncio.Semaphore:
        """Get or create semaphore for a specific user"""
        if user_id not in self.user_semaphores:
            self.user_semaphores[user_id] = asyncio.Semaphore(self.max_concurrent_per_user)
        return self.user_semaphores[user_id]
    
    def _should_apply_concurrency_control(self, path: str) -> bool:
        """Check if concurrency control should be applied to this path"""
        # Apply to resource-intensive operations
        control_paths = {
            "/api/v1/presentations",  # Create presentations
            "/api/v1/presentations/{id}/download",  # Download presentations
        }
        
        # Check exact matches
        if path in control_paths:
            return True
        
        # Check pattern matches
        for control_path in control_paths:
            if control_path.endswith("{id}/download") and path.endswith("/download"):
                return True
        
        return False
    
    async def __call__(self, request: Request, call_next):
        """Middleware function to control concurrency"""
        # Skip concurrency control for certain endpoints
        if not self._should_apply_concurrency_control(request.url.path):
            return await call_next(request)
        
        user_id = self._get_user_id(request)
        user_semaphore = self._get_user_semaphore(user_id)
        
        try:
            # Acquire both global and user-specific semaphores
            async with self.semaphore:
                async with user_semaphore:
                    # Add concurrency info to request state
                    request.state.concurrency_info = {
                        "user_id": user_id,
                        "global_limit": self.max_concurrent_requests,
                        "user_limit": self.max_concurrent_per_user
                    }
                    
                    # Process the request
                    response = await call_next(request)
                    
                    # Add concurrency headers
                    response.headers["X-Concurrency-User-ID"] = user_id
                    response.headers["X-Concurrency-Global-Limit"] = str(self.max_concurrent_requests)
                    response.headers["X-Concurrency-User-Limit"] = str(self.max_concurrent_per_user)
                    
                    return response
                    
        except asyncio.TimeoutError:
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Service temporarily unavailable",
                    "message": "Too many concurrent requests. Please try again later."
                }
            )
    
    def get_concurrency_stats(self) -> Dict[str, Any]:
        """Get current concurrency statistics"""
        return {
            "global_semaphore": {
                "value": self.semaphore._value,
                "locked": self.semaphore.locked()
            },
            "user_semaphores": {
                user_id: {
                    "value": sem._value,
                    "locked": sem.locked()
                }
                for user_id, sem in self.user_semaphores.items()
            },
            "limits": {
                "max_concurrent_requests": self.max_concurrent_requests,
                "max_concurrent_per_user": self.max_concurrent_per_user
            }
        }

# Global concurrency controller instance
concurrency_controller = ConcurrencyController()

# Dependency for getting concurrency info
async def get_concurrency_info(request: Request) -> Optional[Dict[str, Any]]:
    """Dependency to get concurrency information"""
    return getattr(request.state, 'concurrency_info', None) 