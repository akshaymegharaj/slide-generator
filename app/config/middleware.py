"""
Middleware configuration settings
"""
import os
from typing import Dict, Any

class MiddlewareConfig:
    """Configuration for middleware components"""
    
    # Rate Limiting Configuration
    RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    RATE_LIMIT_REQUESTS_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    
    # Authentication Configuration
    API_KEYS = os.getenv("API_KEYS", "").split(",") if os.getenv("API_KEYS") else []
    AUTH_REQUIRED = os.getenv("AUTH_REQUIRED", "false").lower() == "true"
    
    # Concurrency Configuration
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "100"))
    MAX_CONCURRENT_PER_USER = int(os.getenv("MAX_CONCURRENT_PER_USER", "10"))
    
    # Cache Configuration for Rate Limiting
    RATE_LIMIT_CACHE_TTL = int(os.getenv("RATE_LIMIT_CACHE_TTL", "3600"))  # 1 hour
    
    @classmethod
    def get_rate_limit_config(cls) -> Dict[str, Any]:
        """Get rate limiting configuration"""
        return {
            "requests_per_minute": cls.RATE_LIMIT_REQUESTS_PER_MINUTE,
            "requests_per_hour": cls.RATE_LIMIT_REQUESTS_PER_HOUR,
            "cache_ttl": cls.RATE_LIMIT_CACHE_TTL
        }
    
    @classmethod
    def get_auth_config(cls) -> Dict[str, Any]:
        """Get authentication configuration"""
        return {
            "api_keys": cls.API_KEYS,
            "auth_required": cls.AUTH_REQUIRED
        }
    
    @classmethod
    def get_concurrency_config(cls) -> Dict[str, Any]:
        """Get concurrency configuration"""
        return {
            "max_concurrent_requests": cls.MAX_CONCURRENT_REQUESTS,
            "max_concurrent_per_user": cls.MAX_CONCURRENT_PER_USER
        }
    
    @classmethod
    def get_all_config(cls) -> Dict[str, Any]:
        """Get all middleware configuration"""
        return {
            "rate_limiting": cls.get_rate_limit_config(),
            "authentication": cls.get_auth_config(),
            "concurrency": cls.get_concurrency_config()
        } 