"""
Tests for service components
"""
import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from app.services.dummy_llm import DummyLLM
from app.services.cache import CacheService
from app.services.database_storage import DatabaseStorage
from app.services.slide_generator import SlideGenerator
from app.services.factory import service_factory
from app.models.presentation import Presentation, Slide, SlideType
from app.models.database import PresentationDB

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
            assert isinstance(slide, Slide)
            assert slide.title is not None
            assert len(slide.content) > 0
            assert "Test topic" in slide.title or "Test topic" in " ".join(slide.content)
    
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
        assert cache.slide_cache == {}
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
    
    def test_get_slide_cache_hit(self):
        """Test slide cache hit"""
        cache = CacheService()
        slide_id = "slide-1"
        slide_data = {"id": slide_id, "content": "Test slide"}
        
        cache.slide_cache[slide_id] = slide_data
        result = cache.get_slide(slide_id)
        
        assert result == slide_data
    
    def test_get_slide_cache_miss(self):
        """Test slide cache miss"""
        cache = CacheService()
        result = cache.get_slide("nonexistent-slide")
        assert result is None
    
    def test_set_slide(self):
        """Test setting slide in cache"""
        cache = CacheService()
        slide_id = "slide-1"
        slide_data = {"id": slide_id, "content": "Test slide"}
        
        cache.set_slide(slide_id, slide_data)
        assert cache.slide_cache[slide_id] == slide_data
    
    def test_get_api_response_cache_hit(self):
        """Test API response cache hit"""
        cache = CacheService()
        key = "test-key"
        response_data = {"status": "success", "data": "test"}
        
        cache.api_cache[key] = response_data
        result = cache.get_api_response(key)
        
        assert result == response_data
    
    def test_get_api_response_cache_miss(self):
        """Test API response cache miss"""
        cache = CacheService()
        result = cache.get_api_response("nonexistent-key")
        assert result is None
    
    def test_set_api_response(self):
        """Test setting API response in cache"""
        cache = CacheService()
        key = "test-key"
        response_data = {"status": "success", "data": "test"}
        
        cache.set_api_response(key, response_data)
        assert cache.api_cache[key] == response_data
    
    def test_clear_all_caches(self):
        """Test clearing all caches"""
        cache = CacheService()
        
        # Add some data to caches
        cache.presentation_cache["test"] = {"data": "test"}
        cache.slide_cache["test"] = {"data": "test"}
        cache.api_cache["test"] = {"data": "test"}
        
        cache.clear_all()
        
        assert len(cache.presentation_cache) == 0
        assert len(cache.slide_cache) == 0
        assert len(cache.api_cache) == 0
    
    def test_get_cache_stats(self):
        """Test getting cache statistics"""
        cache = CacheService()
        
        # Add some data to caches
        cache.presentation_cache["test1"] = {"data": "test"}
        cache.presentation_cache["test2"] = {"data": "test"}
        cache.slide_cache["slide1"] = {"data": "test"}
        cache.api_cache["api1"] = {"data": "test"}
        
        stats = cache.get_cache_stats()
        
        assert stats["presentation_cache"]["count"] == 2
        assert stats["slide_cache"]["count"] == 1
        assert stats["api_cache"]["count"] == 1

class TestDatabaseStorage:
    """Test database storage service"""
    
    @pytest.mark.asyncio
    async def test_database_storage_initialization(self):
        """Test database storage initialization"""
        cache = CacheService()
        storage = DatabaseStorage(cache)
        assert storage.cache == cache
    
    @pytest.mark.asyncio
    async def test_save_presentation(self, test_session):
        """Test saving presentation to database"""
        cache = CacheService()
        storage = DatabaseStorage(cache)
        
        presentation_data = {
            "id": "test-id",
            "topic": "Test Presentation",
            "num_slides": 3,
            "slides": [
                {"id": "slide-1", "content": "Slide 1 content"},
                {"id": "slide-2", "content": "Slide 2 content"},
                {"id": "slide-3", "content": "Slide 3 content"}
            ],
            "theme": "minimal",
            "aspect_ratio": "16:9"
        }
        
        result = await storage.save_presentation(presentation_data, test_session)
        assert result is True
        
        # Check if it's in cache
        cached = cache.get_presentation("test-id")
        assert cached is not None
        assert cached["topic"] == "Test Presentation"
    
    @pytest.mark.asyncio
    async def test_get_presentation_cache_hit(self, test_session):
        """Test getting presentation from cache"""
        cache = CacheService()
        storage = DatabaseStorage(cache)
        
        presentation_data = {"id": "test-id", "topic": "Test"}
        cache.set_presentation("test-id", presentation_data)
        
        result = await storage.get_presentation("test-id", test_session)
        assert result == presentation_data
    
    @pytest.mark.asyncio
    async def test_get_presentation_database_hit(self, test_session):
        """Test getting presentation from database"""
        cache = CacheService()
        storage = DatabaseStorage(cache)
        
        # Create presentation in database
        presentation_db = PresentationDB(
            id="test-id",
            topic="Test Presentation",
            num_slides=2,
            theme="minimal",
            aspect_ratio="16:9",
            slides_json=json.dumps([
                {"id": "slide-1", "content": "Slide 1"},
                {"id": "slide-2", "content": "Slide 2"}
            ])
        )
        test_session.add(presentation_db)
        await test_session.commit()
        
        result = await storage.get_presentation("test-id", test_session)
        assert result is not None
        assert result["topic"] == "Test Presentation"
        assert len(result["slides"]) == 2
        
        # Should be cached now
        cached = cache.get_presentation("test-id")
        assert cached is not None
    
    @pytest.mark.asyncio
    async def test_get_presentation_not_found(self, test_session):
        """Test getting non-existent presentation"""
        cache = CacheService()
        storage = DatabaseStorage(cache)
        
        result = await storage.get_presentation("nonexistent-id", test_session)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_list_presentations(self, test_session):
        """Test listing presentations"""
        cache = CacheService()
        storage = DatabaseStorage(cache)
        
        # Create some presentations in database
        presentations = [
            PresentationDB(
                id=f"test-{i}",
                topic=f"Test Presentation {i}",
                num_slides=2,
                theme="minimal",
                aspect_ratio="16:9",
                slides_json=json.dumps([{"id": "slide-1", "content": "Slide 1"}])
            )
            for i in range(3)
        ]
        
        for presentation in presentations:
            test_session.add(presentation)
        await test_session.commit()
        
        result = await storage.list_presentations(test_session)
        assert len(result) >= 3
        
        # Check that all presentations have required fields
        for presentation in result:
            assert "id" in presentation
            assert "topic" in presentation
            assert "num_slides" in presentation
            assert "theme" in presentation
            assert "aspect_ratio" in presentation
    
    @pytest.mark.asyncio
    async def test_delete_presentation(self, test_session):
        """Test deleting presentation"""
        cache = CacheService()
        storage = DatabaseStorage(cache)
        
        # Create presentation in database
        presentation_db = PresentationDB(
            id="test-delete",
            topic="Test Delete",
            num_slides=1,
            theme="minimal",
            aspect_ratio="16:9",
            slides_json=json.dumps([{"id": "slide-1", "content": "Slide 1"}])
        )
        test_session.add(presentation_db)
        await test_session.commit()
        
        # Add to cache
        cache.set_presentation("test-delete", {"id": "test-delete", "topic": "Test Delete"})
        
        result = await storage.delete_presentation("test-delete", test_session)
        assert result is True
        
        # Should be removed from cache
        cached = cache.get_presentation("test-delete")
        assert cached is None
        
        # Should be removed from database
        db_result = await storage.get_presentation("test-delete", test_session)
        assert db_result is None

class TestSlideGenerator:
    """Test slide generator service"""
    
    def test_slide_generator_initialization(self):
        """Test slide generator initialization"""
        llm = DummyLLM()
        generator = SlideGenerator(llm)
        assert generator.llm == llm
    
    def test_generate_presentation(self):
        """Test presentation generation"""
        llm = DummyLLM()
        generator = SlideGenerator(llm)
        
        presentation_data = {
            "topic": "Test Topic",
            "num_slides": 3,
            "custom_content": "Custom content for slides"
        }
        
        result = generator.generate_presentation(presentation_data)
        
        assert result["topic"] == "Test Topic"
        assert result["num_slides"] == 3
        assert len(result["slides"]) == 3
        assert "id" in result
        assert "theme" in result
        assert "aspect_ratio" in result
        
        # Check slides
        for i, slide in enumerate(result["slides"]):
            assert slide["id"] == f"slide-{i+1}"
            assert "content" in slide
            assert "title" in slide
    
    def test_generate_presentation_with_aspect_ratio(self):
        """Test presentation generation with specific aspect ratio"""
        llm = DummyLLM()
        generator = SlideGenerator(llm)
        
        presentation_data = {
            "topic": "Test Topic",
            "num_slides": 2,
            "aspect_ratio": "4:3"
        }
        
        result = generator.generate_presentation(presentation_data)
        
        assert result["aspect_ratio"] == "4:3"
        assert result["custom_width"] is None
        assert result["custom_height"] is None
    
    def test_generate_presentation_custom_aspect_ratio(self):
        """Test presentation generation with custom aspect ratio"""
        llm = DummyLLM()
        generator = SlideGenerator(llm)
        
        presentation_data = {
            "topic": "Test Topic",
            "num_slides": 2,
            "aspect_ratio": "custom",
            "custom_width": 12.0,
            "custom_height": 8.0
        }
        
        result = generator.generate_presentation(presentation_data)
        
        assert result["aspect_ratio"] == "custom"
        assert result["custom_width"] == 12.0
        assert result["custom_height"] == 8.0
    
    def test_generate_slide_content(self):
        """Test slide content generation"""
        llm = DummyLLM()
        generator = SlideGenerator(llm)
        
        content = generator._generate_slide_content("Test Topic", 1, 3)
        
        assert isinstance(content, str)
        assert len(content) > 0
        assert "Test Topic" in content
    
    def test_generate_slide_title(self):
        """Test slide title generation"""
        llm = DummyLLM()
        generator = SlideGenerator(llm)
        
        title = generator._generate_slide_title("Test Topic", 1, 3)
        
        assert isinstance(title, str)
        assert len(title) > 0
        assert "Test Topic" in title

class TestServiceFactory:
    """Test service factory"""
    
    def test_service_factory_initialization(self):
        """Test service factory initialization"""
        factory = service_factory
        assert factory.cache_service is not None
        assert factory.llm_service is not None
        assert factory.storage_service is not None
    
    def test_set_cache_service(self):
        """Test setting cache service"""
        factory = service_factory
        new_cache = CacheService()
        
        factory.set_cache_service(new_cache)
        assert factory.cache_service == new_cache
    
    def test_set_llm_service(self):
        """Test setting LLM service"""
        factory = service_factory
        new_llm = DummyLLM()
        
        factory.set_llm_service(new_llm)
        assert factory.llm_service == new_llm
    
    def test_set_storage_service(self):
        """Test setting storage service"""
        factory = service_factory
        new_storage = DatabaseStorage(CacheService())
        
        factory.set_storage_service(new_storage)
        assert factory.storage_service == new_storage
    
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
    
    def test_get_storage_service(self):
        """Test getting storage service"""
        factory = service_factory
        storage = factory.get_storage_service()
        assert storage is not None
        assert isinstance(storage, DatabaseStorage) 