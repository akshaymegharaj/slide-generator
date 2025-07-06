"""
Caching service for in-memory caching
"""
from cachetools import TTLCache, LRUCache
from typing import Optional, Any, Dict
import hashlib
import json

from app.interfaces.cache import CacheInterface

class CacheService(CacheInterface):
    """Service for in-memory caching"""
    
    def __init__(self):
        # Cache for presentations (TTL: 1 hour, max 100 items)
        self.presentation_cache = TTLCache(maxsize=100, ttl=3600)
        
        # Cache for slide generation results (TTL: 30 minutes, max 200 items)
        self.slide_cache = TTLCache(maxsize=200, ttl=1800)
        
        # Cache for API responses (TTL: 15 minutes, max 500 items)
        self.api_cache = TTLCache(maxsize=500, ttl=900)
    
    def _generate_cache_key(self, *args, **kwargs) -> str:
        """Generate a cache key from arguments"""
        # Convert args and kwargs to a string and hash it
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_presentation(self, presentation_id: str) -> Optional[Dict]:
        """Get presentation from cache"""
        return self.presentation_cache.get(presentation_id)
    
    def set_presentation(self, presentation_id: str, presentation_data: Dict) -> None:
        """Store presentation in cache"""
        self.presentation_cache[presentation_id] = presentation_data
    
    def delete_presentation(self, presentation_id: str) -> None:
        """Remove presentation from cache"""
        self.presentation_cache.pop(presentation_id, None)
    
    def get_slide_generation(self, topic: str, num_slides: int, custom_content: Optional[str] = None, **kwargs) -> Optional[Dict[str, Any]]:
        """Get slide generation result from cache"""
        cache_key = self._generate_cache_key(topic, num_slides, custom_content, **kwargs)
        return self.slide_cache.get(cache_key)
    
    def set_slide_generation(self, topic: str, num_slides: int, custom_content: Optional[str] = None, result: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Store slide generation result in cache"""
        cache_key = self._generate_cache_key(topic, num_slides, custom_content, **kwargs)
        if result is not None:
            self.slide_cache[cache_key] = result
    
    def get_api_response(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Get API response from cache"""
        cache_key = self._generate_cache_key(endpoint, params or {})
        return self.api_cache.get(cache_key)
    
    def set_api_response(self, endpoint: str, params: Optional[Dict[str, Any]] = None, response: Optional[Dict[str, Any]] = None) -> None:
        """Store API response in cache"""
        cache_key = self._generate_cache_key(endpoint, params or {})
        if response is not None:
            self.api_cache[cache_key] = response
    
    def clear_all(self) -> None:
        """Clear all caches"""
        self.presentation_cache.clear()
        self.slide_cache.clear()
        self.api_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'presentation_cache': {
                'size': len(self.presentation_cache),
                'maxsize': self.presentation_cache.maxsize,
                'ttl': self.presentation_cache.ttl
            },
            'slide_cache': {
                'size': len(self.slide_cache),
                'maxsize': self.slide_cache.maxsize,
                'ttl': self.slide_cache.ttl
            },
            'api_cache': {
                'size': len(self.api_cache),
                'maxsize': self.api_cache.maxsize,
                'ttl': self.api_cache.ttl
            }
        } 