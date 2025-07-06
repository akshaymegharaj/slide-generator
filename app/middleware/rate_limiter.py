"""
Rate Limiting Middleware
Uses the existing cache system to implement rate limiting
"""
import time
from typing import Dict, Optional, Any
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.services.factory import service_factory

class RateLimiter:
    """Rate limiting middleware using cache system"""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.cache = service_factory.get_cache_service()
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check for forwarded headers (for proxy/load balancer setups)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection IP
        return request.client.host if request.client else "unknown"
    
    def _get_rate_limit_key(self, client_ip: str, window: str) -> str:
        """Generate cache key for rate limiting"""
        current_time = int(time.time())
        if window == "minute":
            # Round to minute boundary
            window_time = current_time - (current_time % 60)
        else:  # hour
            # Round to hour boundary
            window_time = current_time - (current_time % 3600)
        
        return f"rate_limit:{client_ip}:{window}:{window_time}"
    
    def _check_rate_limit(self, client_ip: str) -> Dict[str, Any]:
        """Check if client has exceeded rate limits"""
        # Check minute limit
        minute_key = self._get_rate_limit_key(client_ip, "minute")
        minute_data = self.cache.get_api_response(minute_key, {})
        minute_requests = minute_data.get("count", 0) if isinstance(minute_data, dict) else 0
        
        # Check hour limit
        hour_key = self._get_rate_limit_key(client_ip, "hour")
        hour_data = self.cache.get_api_response(hour_key, {})
        hour_requests = hour_data.get("count", 0) if isinstance(hour_data, dict) else 0
        
        # Check limits
        minute_exceeded = minute_requests >= self.requests_per_minute
        hour_exceeded = hour_requests >= self.requests_per_hour
        
        return {
            "minute_requests": minute_requests,
            "hour_requests": hour_requests,
            "minute_limit": self.requests_per_minute,
            "hour_limit": self.requests_per_hour,
            "minute_exceeded": minute_exceeded,
            "hour_exceeded": hour_exceeded,
            "minute_key": minute_key,
            "hour_key": hour_key
        }
    
    def _increment_rate_limit(self, client_ip: str, minute_key: str, hour_key: str):
        """Increment request counters"""
        # Increment minute counter
        minute_data = self.cache.get_api_response(minute_key, {})
        current_minute = minute_data.get("count", 0) if isinstance(minute_data, dict) else 0
        self.cache.set_api_response(minute_key, {}, {"count": current_minute + 1})
        
        # Increment hour counter
        hour_data = self.cache.get_api_response(hour_key, {})
        current_hour = hour_data.get("count", 0) if isinstance(hour_data, dict) else 0
        self.cache.set_api_response(hour_key, {}, {"count": current_hour + 1})
    
    async def __call__(self, request: Request, call_next):
        """Middleware function to check rate limits"""
        client_ip = self._get_client_ip(request)
        
        # Check rate limits
        rate_info = self._check_rate_limit(client_ip)
        
        if rate_info["minute_exceeded"]:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {self.requests_per_minute} per minute",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        if rate_info["hour_exceeded"]:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {self.requests_per_hour} per hour",
                    "retry_after": 3600
                },
                headers={"Retry-After": "3600"}
            )
        
        # Increment counters
        self._increment_rate_limit(client_ip, rate_info["minute_key"], rate_info["hour_key"])
        
        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Minute-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Minute-Remaining"] = str(self.requests_per_minute - rate_info["minute_requests"])
        response.headers["X-RateLimit-Hour-Limit"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Hour-Remaining"] = str(self.requests_per_hour - rate_info["hour_requests"])
        
        return response

# Global rate limiter instance
rate_limiter = RateLimiter() 