"""
Demonstration of modular architecture - showing how easy it is to swap implementations
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.factory import service_factory
from app.services.slide_generator import SlideGenerator
from app.database import create_db_and_tables, AsyncSessionLocal
from app.models.presentation import PresentationCreate, Presentation
from app.services.examples.openai_llm import OpenAILLM
from app.services.examples.redis_cache import RedisCacheService

async def demo_modular_architecture():
    """Demonstrate the modular architecture"""
    print("🏗️  Modular Architecture Demonstration")
    print("=" * 50)
    
    # Initialize database
    print("📊 Setting up database...")
    await create_db_and_tables()
    
    # Demo 1: Default implementations
    print("\n1️⃣ Using default implementations (Dummy LLM + In-Memory Cache)")
    print("-" * 50)
    
    # Get default services
    cache_service = service_factory.get_cache_service()
    storage_service = service_factory.get_storage_service()
    llm_service = service_factory.get_llm_service()
    slide_generator = SlideGenerator(cache_service, llm_service)
    
    # Create a presentation with default services
    async with AsyncSessionLocal() as session:
        presentation_data = PresentationCreate(
            topic="Machine Learning Basics",
            num_slides=2,
            custom_content="Focus on practical applications"
        )
        
        # Generate slides
        slides = await slide_generator.generate_slides(
            topic=presentation_data.topic,
            num_slides=presentation_data.num_slides,
            custom_content=presentation_data.custom_content
        )
        
        # Create presentation
        presentation = Presentation(
            id="demo-1",
            topic=presentation_data.topic,
            num_slides=presentation_data.num_slides,
            slides=slides,
            custom_content=presentation_data.custom_content
        )
        
        # Save to storage
        success = await storage_service.save_presentation(session, presentation)
        print(f"   ✅ Presentation created with default services: {success}")
        
        # Check cache stats
        cache_stats = cache_service.get_cache_stats()
        print(f"   📈 Cache stats: {cache_stats['presentation_cache']['size']} presentations cached")
    
    # Demo 2: Swap to OpenAI LLM (if API key is available)
    print("\n2️⃣ Swapping to OpenAI LLM implementation")
    print("-" * 50)
    
    # Check if OpenAI API key is available
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        print("   🔄 Swapping LLM service to OpenAI...")
        
        # Create OpenAI LLM instance
        openai_llm = OpenAILLM(api_key=openai_api_key)
        
        # Swap the LLM service
        service_factory.set_llm_service(openai_llm)
        
        # Get updated services
        llm_service = service_factory.get_llm_service()
        slide_generator = SlideGenerator(cache_service, llm_service)
        
        print("   ✅ Successfully swapped to OpenAI LLM")
        
        # Create another presentation with OpenAI
        async with AsyncSessionLocal() as session:
            presentation_data = PresentationCreate(
                topic="Artificial Intelligence Trends",
                num_slides=2,
                custom_content="Focus on recent developments"
            )
            
            slides = await slide_generator.generate_slides(
                topic=presentation_data.topic,
                num_slides=presentation_data.num_slides,
                custom_content=presentation_data.custom_content
            )
            
            presentation = Presentation(
                id="demo-2",
                topic=presentation_data.topic,
                num_slides=presentation_data.num_slides,
                slides=slides,
                custom_content=presentation_data.custom_content
            )
            
            success = await storage_service.save_presentation(session, presentation)
            print(f"   ✅ Presentation created with OpenAI LLM: {success}")
    else:
        print("   ⚠️  OpenAI API key not found. Skipping OpenAI demo.")
        print("   💡 Set OPENAI_API_KEY environment variable to test OpenAI integration")
    
    # Demo 3: Swap to Redis Cache (if Redis is available)
    print("\n3️⃣ Swapping to Redis Cache implementation")
    print("-" * 50)
    
    try:
        # Try to create Redis cache instance
        redis_cache = RedisCacheService()
        
        # Test Redis connection
        await redis_cache.get_cache_stats()
        
        print("   🔄 Swapping cache service to Redis...")
        
        # Swap the cache service
        service_factory.set_cache_service(redis_cache)
        
        # Get updated services
        cache_service = service_factory.get_cache_service()
        storage_service = service_factory.get_storage_service()
        slide_generator = SlideGenerator(cache_service, llm_service)
        
        print("   ✅ Successfully swapped to Redis Cache")
        
        # Test with Redis cache
        async with AsyncSessionLocal() as session:
            # Retrieve existing presentation
            presentation = await storage_service.get_presentation(session, "demo-1")
            if presentation:
                print(f"   📋 Retrieved presentation from Redis-backed storage: {presentation.topic}")
                
                # Check Redis cache stats
                cache_stats = await cache_service.get_cache_stats()
                print(f"   📈 Redis cache stats: {cache_stats['presentation_cache']['size']} presentations cached")
        
    except Exception as e:
        print(f"   ⚠️  Redis not available: {e}")
        print("   💡 Install Redis and redis-py to test Redis integration")
    
    # Demo 4: Reset to default implementations
    print("\n4️⃣ Resetting to default implementations")
    print("-" * 50)
    
    service_factory.reset_services()
    
    # Get default services again
    cache_service = service_factory.get_cache_service()
    storage_service = service_factory.get_storage_service()
    llm_service = service_factory.get_llm_service()
    
    print("   ✅ Reset to default implementations")
    print(f"   🧠 LLM Service: {type(llm_service).__name__}")
    print(f"   💾 Cache Service: {type(cache_service).__name__}")
    print(f"   🗄️  Storage Service: {type(storage_service).__name__}")
    
    # Demo 5: Show how to create custom implementations
    print("\n5️⃣ Creating custom implementations")
    print("-" * 50)
    
    # Example of creating a custom cache implementation
    class CustomCache:
        def __init__(self):
            self.data = {}
        
        def get_presentation(self, presentation_id: str):
            return self.data.get(f"presentation:{presentation_id}")
        
        def set_presentation(self, presentation_id: str, presentation_data):
            self.data[f"presentation:{presentation_id}"] = presentation_data
        
        def delete_presentation(self, presentation_id: str):
            self.data.pop(f"presentation:{presentation_id}", None)
        
        def get_slide_generation(self, topic: str, num_slides: int, custom_content=None, **kwargs):
            key = f"slide_gen:{topic}:{num_slides}:{custom_content}"
            return self.data.get(key)
        
        def set_slide_generation(self, topic: str, num_slides: int, custom_content=None, result=None, **kwargs):
            if result is not None:
                key = f"slide_gen:{topic}:{num_slides}:{custom_content}"
                self.data[key] = result
        
        def get_api_response(self, endpoint: str, params=None):
            key = f"api:{endpoint}:{params}"
            return self.data.get(key)
        
        def set_api_response(self, endpoint: str, params=None, response=None):
            if response is not None:
                key = f"api:{endpoint}:{params}"
                self.data[key] = response
        
        def clear_all(self):
            self.data.clear()
        
        def get_cache_stats(self):
            return {
                'presentation_cache': {'size': len([k for k in self.data.keys() if k.startswith('presentation:')]), 'type': 'custom'},
                'slide_cache': {'size': len([k for k in self.data.keys() if k.startswith('slide_gen:')]), 'type': 'custom'},
                'api_cache': {'size': len([k for k in self.data.keys() if k.startswith('api:')]), 'type': 'custom'}
            }
    
    # Use custom cache
    custom_cache = CustomCache()
    service_factory.set_cache_service(custom_cache)
    
    print("   ✅ Created and set custom cache implementation")
    
    # Test custom cache
    custom_cache.set_presentation("test", {"topic": "Test Presentation"})
    cached = custom_cache.get_presentation("test")
    print(f"   📋 Custom cache test: {cached['topic'] if cached else 'Not found'}")
    
    print("\n🎉 Modular Architecture Demo Completed!")
    print("=" * 50)
    print("\nKey Benefits Demonstrated:")
    print("✅ Easy swapping of LLM providers (Dummy → OpenAI)")
    print("✅ Easy swapping of cache backends (In-Memory → Redis)")
    print("✅ Easy creation of custom implementations")
    print("✅ No code changes required in main application")
    print("✅ Dependency injection through service factory")
    print("✅ Interface-based design for loose coupling")

if __name__ == "__main__":
    asyncio.run(demo_modular_architecture()) 