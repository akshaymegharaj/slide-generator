"""
Simplified tests for service components
"""
import pytest
from app.services.dummy_llm import DummyLLM
from app.services.cache import CacheService
from app.services.factory import service_factory
from app.models.presentation import SlideType

class TestDummyLLM:
    """Test dummy LLM service"""
    
    def test_dummy_llm_initialization(self):
        """Test dummy LLM initialization"""
        llm = DummyLLM()
        assert llm.delay_simulation == 0.1
    
    @pytest.mark.asyncio
    async def test_generate_slides_content(self):
        """Test slide content generation"""
        llm = DummyLLM()
        slides = await llm.generate_slides_content("Test topic", 3)
        
        assert isinstance(slides, list)
        assert len(slides) == 3
        
        for slide in slides:
            assert slide.title is not None
            assert len(slide.content) > 0
    
    @pytest.mark.asyncio
    async def test_generate_slide_title(self):
        """Test slide title generation"""
        llm = DummyLLM()
        title = await llm.generate_slide_title("Test topic", 1, SlideType.BULLET_POINTS)
        
        assert isinstance(title, str)
        assert len(title) > 0
        assert "Key Point 1" in title
    
    @pytest.mark.asyncio
    async def test_generate_citations(self):
        """Test citation generation"""
        llm = DummyLLM()
        content = ["Test content 1", "Test content 2"]
        citations = await llm.generate_citations("Test topic", content)
        
        assert isinstance(citations, list)
        assert len(citations) > 0
        
        for citation in citations:
            assert isinstance(citation, str)
            assert "Test topic" in citation

class TestCacheService:
    """Test cache service"""
    
    def test_cache_service_initialization(self):
        """Test cache service initialization"""
        cache = CacheService()
        assert cache.presentation_cache == {}
        assert cache.api_cache == {}
    
    def test_get_presentation_cache_hit(self):
        """Test presentation cache hit"""
        cache = CacheService()
        presentation_id = "test-id"
        presentation_data = {"id": presentation_id, "topic": "Test"}
        
        cache.presentation_cache[presentation_id] = presentation_data
        result = cache.get_presentation(presentation_id)
        
        assert result == presentation_data
    
    def test_get_presentation_cache_miss(self):
        """Test presentation cache miss"""
        cache = CacheService()
        result = cache.get_presentation("nonexistent-id")
        assert result is None
    
    def test_set_presentation(self):
        """Test setting presentation in cache"""
        cache = CacheService()
        presentation_id = "test-id"
        presentation_data = {"id": presentation_id, "topic": "Test"}
        
        cache.set_presentation(presentation_id, presentation_data)
        assert cache.presentation_cache[presentation_id] == presentation_data
    
    def test_get_api_response_cache_hit(self):
        """Test API response cache hit"""
        cache = CacheService()
        endpoint = "test-endpoint"
        params = {"param1": "value1"}
        response_data = {"status": "success", "data": "test"}
        
        cache.set_api_response(endpoint, params, response_data)
        result = cache.get_api_response(endpoint, params)
        
        assert result == response_data
    
    def test_get_api_response_cache_miss(self):
        """Test API response cache miss"""
        cache = CacheService()
        result = cache.get_api_response("nonexistent-endpoint")
        assert result is None
    
    def test_set_api_response(self):
        """Test setting API response in cache"""
        cache = CacheService()
        endpoint = "test-endpoint"
        params = {"param1": "value1"}
        response_data = {"status": "success", "data": "test"}
        
        cache.set_api_response(endpoint, params, response_data)
        result = cache.get_api_response(endpoint, params)
        assert result == response_data
    
    def test_clear_all_caches(self):
        """Test clearing all caches"""
        cache = CacheService()
        
        # Add some data to caches
        cache.presentation_cache["test"] = {"data": "test"}
        cache.api_cache["test"] = {"data": "test"}
        
        cache.clear_all()
        
        assert len(cache.presentation_cache) == 0
        assert len(cache.api_cache) == 0
    
    def test_get_cache_stats(self):
        """Test getting cache statistics"""
        cache = CacheService()
        
        # Add some data to caches
        cache.set_presentation("test1", {"data": "test"})
        cache.set_presentation("test2", {"data": "test"})
        cache.set_api_response("api1", {}, {"data": "test"})
        
        stats = cache.get_cache_stats()
        
        assert stats["presentation_cache"]["size"] == 2
        assert stats["api_cache"]["size"] == 1

class TestServiceFactory:
    """Test service factory"""
    
    def test_service_factory_initialization(self):
        """Test service factory initialization"""
        factory = service_factory
        cache = factory.get_cache_service()
        llm = factory.get_llm_service()
        storage = factory.get_storage_service()
        
        assert cache is not None
        assert llm is not None
        assert storage is not None
    
    def test_set_cache_service(self):
        """Test setting cache service"""
        factory = service_factory
        new_cache = CacheService()
        
        factory.set_cache_service(new_cache)
        assert factory.get_cache_service() == new_cache
    
    def test_set_llm_service(self):
        """Test setting LLM service"""
        factory = service_factory
        new_llm = DummyLLM()
        
        factory.set_llm_service(new_llm)
        assert factory.get_llm_service() == new_llm
    
    def test_get_cache_service(self):
        """Test getting cache service"""
        factory = service_factory
        cache = factory.get_cache_service()
        assert cache is not None
        assert isinstance(cache, CacheService)
    
    def test_get_llm_service(self):
        """Test getting LLM service"""
        factory = service_factory
        llm = factory.get_llm_service()
        assert llm is not None
        assert isinstance(llm, DummyLLM) 