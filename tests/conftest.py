"""
Pytest configuration and fixtures
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_session
from app.services.factory import service_factory
from app.services.dummy_llm import DummyLLM
from app.services.cache import CacheService
from app.services.database_storage import DatabaseStorage

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_slide_generator.db"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()

@pytest.fixture(scope="session")
async def test_session_maker(test_engine):
    """Create test session maker."""
    async_session_maker = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    yield async_session_maker

@pytest.fixture
async def test_session(test_session_maker):
    """Create test database session."""
    async with test_session_maker() as session:
        yield session

@pytest.fixture
def client(test_session):
    """Create test client with dependency override."""
    def override_get_session():
        return test_session
    
    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def mock_services():
    """Mock services for testing."""
    # Create test cache service
    cache_service = CacheService()
    
    # Create test LLM service
    llm_service = DummyLLM()
    
    # Create test storage service
    storage_service = DatabaseStorage(cache_service)
    
    # Set services in factory
    service_factory.set_cache_service(cache_service)
    service_factory.set_llm_service(llm_service)
    service_factory.set_storage_service(storage_service)
    
    return {
        "cache": cache_service,
        "llm": llm_service,
        "storage": storage_service
    }

@pytest.fixture
def sample_presentation_data():
    """Sample presentation data for testing."""
    return {
        "topic": "Test Presentation",
        "num_slides": 3,
        "custom_content": "Test content for slides"
    }

@pytest.fixture
def sample_presentation_config():
    """Sample presentation configuration for testing."""
    return {
        "theme": "minimal",
        "font": "Arial",
        "colors": {
            "primary": "#FF0000",
            "secondary": "#00FF00",
            "background": "#FFFFFF",
            "text": "#000000"
        },
        "aspect_ratio": "16:9"
    }

@pytest.fixture
def sample_custom_aspect_ratio():
    """Sample custom aspect ratio for testing."""
    return {
        "aspect_ratio": "custom",
        "custom_width": 12.0,
        "custom_height": 8.0
    } 