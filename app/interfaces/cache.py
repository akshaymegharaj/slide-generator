"""
Abstract cache interface for different caching backends
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class CacheInterface(ABC):
    """Abstract interface for caching operations"""
    
    @abstractmethod
    def get_presentation(self, presentation_id: str) -> Optional[Dict[str, Any]]:
        """Get presentation from cache"""
        pass
    
    @abstractmethod
    def set_presentation(self, presentation_id: str, presentation_data: Dict[str, Any]) -> None:
        """Store presentation in cache"""
        pass
    
    @abstractmethod
    def delete_presentation(self, presentation_id: str) -> None:
        """Remove presentation from cache"""
        pass
    
    @abstractmethod
    def get_slide_generation(self, topic: str, num_slides: int, custom_content: Optional[str] = None, **kwargs) -> Optional[Dict[str, Any]]:
        """Get slide generation result from cache"""
        pass
    
    @abstractmethod
    def set_slide_generation(self, topic: str, num_slides: int, custom_content: Optional[str] = None, result: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Store slide generation result in cache"""
        pass
    
    @abstractmethod
    def get_api_response(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Get API response from cache"""
        pass
    
    @abstractmethod
    def set_api_response(self, endpoint: str, params: Optional[Dict[str, Any]] = None, response: Optional[Dict[str, Any]] = None) -> None:
        """Store API response in cache"""
        pass
    
    @abstractmethod
    def clear_all(self) -> None:
        """Clear all caches"""
        pass
    
    @abstractmethod
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        pass 