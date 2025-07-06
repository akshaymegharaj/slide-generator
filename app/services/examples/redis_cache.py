"""
Example Redis cache implementation
This shows how easy it is to swap cache backends
"""
import json
import hashlib
from typing import Optional, Dict, Any
import redis.asyncio as redis

from app.interfaces.cache import CacheInterface

class RedisCacheService(CacheInterface):
    """Redis-based cache implementation"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url)
        self.default_ttl = 3600  # 1 hour default
    
    def _generate_cache_key(self, *args, **kwargs) -> str:
        """Generate a cache key from arguments"""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def get_presentation(self, presentation_id: str) -> Optional[Dict[str, Any]]:
        """Get presentation from Redis cache"""
        try:
            data = await self.redis.get(f"presentation:{presentation_id}")
            return json.loads(data) if data else None
        except Exception:
            return None
    
    async def set_presentation(self, presentation_id: str, presentation_data: Dict[str, Any]) -> None:
        """Store presentation in Redis cache"""
        try:
            await self.redis.setex(
                f"presentation:{presentation_id}",
                self.default_ttl,
                json.dumps(presentation_data)
            )
        except Exception:
            pass  # Fail silently
    
    async def delete_presentation(self, presentation_id: str) -> None:
        """Remove presentation from Redis cache"""
        try:
            await self.redis.delete(f"presentation:{presentation_id}")
        except Exception:
            pass
    
    async def get_slide_generation(self, topic: str, num_slides: int, custom_content: Optional[str] = None, **kwargs) -> Optional[Dict[str, Any]]:
        """Get slide generation result from Redis cache"""
        try:
            cache_key = self._generate_cache_key(topic, num_slides, custom_content, **kwargs)
            data = await self.redis.get(f"slide_gen:{cache_key}")
            return json.loads(data) if data else None
        except Exception:
            return None
    
    async def set_slide_generation(self, topic: str, num_slides: int, custom_content: Optional[str] = None, result: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Store slide generation result in Redis cache"""
        try:
            cache_key = self._generate_cache_key(topic, num_slides, custom_content, **kwargs)
            if result is not None:
                await self.redis.setex(
                    f"slide_gen:{cache_key}",
                    self.default_ttl // 2,  # 30 minutes for slide generation
                    json.dumps(result)
                )
        except Exception:
            pass
    
    async def get_api_response(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Get API response from Redis cache"""
        try:
            cache_key = self._generate_cache_key(endpoint, params or {})
            data = await self.redis.get(f"api:{cache_key}")
            return json.loads(data) if data else None
        except Exception:
            return None
    
    async def set_api_response(self, endpoint: str, params: Optional[Dict[str, Any]] = None, response: Optional[Dict[str, Any]] = None) -> None:
        """Store API response in Redis cache"""
        try:
            cache_key = self._generate_cache_key(endpoint, params or {})
            if response is not None:
                await self.redis.setex(
                    f"api:{cache_key}",
                    self.default_ttl // 4,  # 15 minutes for API responses
                    json.dumps(response)
                )
        except Exception:
            pass
    
    async def clear_all(self) -> None:
        """Clear all caches from Redis"""
        try:
            # Clear all keys with our prefixes
            async for key in self.redis.scan_iter(match="presentation:*"):
                await self.redis.delete(key)
            async for key in self.redis.scan_iter(match="slide_gen:*"):
                await self.redis.delete(key)
            async for key in self.redis.scan_iter(match="api:*"):
                await self.redis.delete(key)
        except Exception:
            pass
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics"""
        try:
            presentation_keys = len([k async for k in self.redis.scan_iter(match="presentation:*")])
            slide_keys = len([k async for k in self.redis.scan_iter(match="slide_gen:*")])
            api_keys = len([k async for k in self.redis.scan_iter(match="api:*")])
            
            return {
                'presentation_cache': {
                    'size': presentation_keys,
                    'type': 'redis'
                },
                'slide_cache': {
                    'size': slide_keys,
                    'type': 'redis'
                },
                'api_cache': {
                    'size': api_keys,
                    'type': 'redis'
                }
            }
        except Exception:
            return {
                'presentation_cache': {'size': 0, 'type': 'redis'},
                'slide_cache': {'size': 0, 'type': 'redis'},
                'api_cache': {'size': 0, 'type': 'redis'}
            } 