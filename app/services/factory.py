"""
Service factory for dependency injection and easy implementation swapping
"""
from typing import Optional
from app.interfaces.storage import StorageInterface
from app.interfaces.cache import CacheInterface
from app.interfaces.llm import LLMInterface
from app.services.cache import CacheService
from app.services.database_storage import DatabaseStorage
from app.services.dummy_llm import DummyLLM

class ServiceFactory:
    """Factory for creating and managing service instances"""
    
    def __init__(self):
        self._cache_service: Optional[CacheInterface] = None
        self._storage_service: Optional[StorageInterface] = None
        self._llm_service: Optional[LLMInterface] = None
    
    def get_cache_service(self) -> CacheInterface:
        """Get or create cache service instance"""
        if self._cache_service is None:
            self._cache_service = CacheService()
        return self._cache_service
    
    def get_storage_service(self) -> StorageInterface:
        """Get or create storage service instance"""
        if self._storage_service is None:
            cache_service = self.get_cache_service()
            self._storage_service = DatabaseStorage(cache_service)
        return self._storage_service
    
    def get_llm_service(self) -> LLMInterface:
        """Get or create LLM service instance"""
        if self._llm_service is None:
            self._llm_service = DummyLLM()
        return self._llm_service
    
    def set_cache_service(self, cache_service: CacheInterface) -> None:
        """Set a custom cache service implementation"""
        self._cache_service = cache_service
    
    def set_storage_service(self, storage_service: StorageInterface) -> None:
        """Set a custom storage service implementation"""
        self._storage_service = storage_service
    
    def set_llm_service(self, llm_service: LLMInterface) -> None:
        """Set a custom LLM service implementation"""
        self._llm_service = llm_service
    
    def reset_services(self) -> None:
        """Reset all services to default implementations"""
        self._cache_service = None
        self._storage_service = None
        self._llm_service = None

# Global service factory instance
service_factory = ServiceFactory() 