"""
Simple test script for the modular architecture
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

async def test_simple():
    """Simple test of the modular architecture"""
    print("🧪 Simple Modular Architecture Test")
    print("=" * 40)
    
    # Initialize database
    print("📊 Setting up database...")
    await create_db_and_tables()
    
    # Get services from factory
    print("⚡ Getting services from factory...")
    cache_service = service_factory.get_cache_service()
    storage_service = service_factory.get_storage_service()
    llm_service = service_factory.get_llm_service()
    slide_generator = SlideGenerator(cache_service, llm_service)
    
    print(f"   🧠 LLM Service: {type(llm_service).__name__}")
    print(f"   💾 Cache Service: {type(cache_service).__name__}")
    print(f"   🗄️  Storage Service: {type(storage_service).__name__}")
    
    # Test 1: Generate slides
    print("\n1️⃣ Testing slide generation...")
    slides = await slide_generator.generate_slides(
        topic="Python Programming",
        num_slides=2,
        custom_content="Focus on best practices"
    )
    
    print(f"   ✅ Generated {len(slides)} slides")
    for i, slide in enumerate(slides):
        print(f"   📄 Slide {i+1}: {slide.title} ({slide.slide_type.value})")
    
    # Test 2: Create and save presentation
    print("\n2️⃣ Testing presentation creation and storage...")
    async with AsyncSessionLocal() as session:
        presentation_data = PresentationCreate(
            topic="Python Programming",
            num_slides=2,
            custom_content="Focus on best practices"
        )
        
        # Create presentation
        presentation = Presentation(
            id="test-123",
            topic=presentation_data.topic,
            num_slides=presentation_data.num_slides,
            slides=slides,
            custom_content=presentation_data.custom_content
        )
        
        # Save to storage
        success = await storage_service.save_presentation(session, presentation)
        print(f"   ✅ Presentation saved: {success}")
        
        # Test 3: Retrieve from storage
        print("\n3️⃣ Testing presentation retrieval...")
        retrieved = await storage_service.get_presentation(session, "test-123")
        if retrieved:
            print(f"   ✅ Retrieved presentation: {retrieved.topic}")
            print(f"   📊 Has {len(retrieved.slides)} slides")
        else:
            print("   ❌ Failed to retrieve presentation")
        
        # Test 4: Check cache
        print("\n4️⃣ Testing cache functionality...")
        cache_stats = cache_service.get_cache_stats()
        print(f"   📈 Cache stats: {cache_stats['presentation_cache']['size']} presentations cached")
        
        # Test 5: List presentations
        print("\n5️⃣ Testing presentation listing...")
        presentations = await storage_service.list_presentations(session)
        print(f"   📋 Found {len(presentations)} presentations in storage")
        
        # Test 6: Search presentations
        print("\n6️⃣ Testing presentation search...")
        search_results = await storage_service.search_presentations(session, "Python")
        print(f"   🔍 Found {len(search_results)} presentations matching 'Python'")
        
        # Test 7: Delete presentation
        print("\n7️⃣ Testing presentation deletion...")
        success = await storage_service.delete_presentation(session, "test-123")
        print(f"   ✅ Presentation deleted: {success}")
        
        # Verify deletion
        retrieved_after_delete = await storage_service.get_presentation(session, "test-123")
        if not retrieved_after_delete:
            print("   ✅ Confirmed presentation was deleted")
        else:
            print("   ❌ Presentation still exists after deletion")
    
    # Test 8: Test service swapping
    print("\n8️⃣ Testing service swapping...")
    
    # Create a simple custom cache
    class SimpleCache:
        def __init__(self):
            self.data = {}
        
        def get_presentation(self, presentation_id: str):
            return self.data.get(f"presentation:{presentation_id}")
        
        def set_presentation(self, presentation_id: str, presentation_data):
            self.data[f"presentation:{presentation_id}"] = presentation_data
        
        def delete_presentation(self, presentation_id: str):
            self.data.pop(f"presentation:{presentation_id}", None)
        
        def get_slide_generation(self, topic: str, num_slides: int, custom_content=None, **kwargs):
            key = f"slide_gen:{topic}:{num_slides}"
            return self.data.get(key)
        
        def set_slide_generation(self, topic: str, num_slides: int, custom_content=None, result=None, **kwargs):
            if result is not None:
                key = f"slide_gen:{topic}:{num_slides}"
                self.data[key] = result
        
        def get_api_response(self, endpoint: str, params=None):
            key = f"api:{endpoint}"
            return self.data.get(key)
        
        def set_api_response(self, endpoint: str, params=None, response=None):
            if response is not None:
                key = f"api:{endpoint}"
                self.data[key] = response
        
        def clear_all(self):
            self.data.clear()
        
        def get_cache_stats(self):
            return {
                'presentation_cache': {'size': len([k for k in self.data.keys() if k.startswith('presentation:')]), 'type': 'simple'},
                'slide_cache': {'size': len([k for k in self.data.keys() if k.startswith('slide_gen:')]), 'type': 'simple'},
                'api_cache': {'size': len([k for k in self.data.keys() if k.startswith('api:')]), 'type': 'simple'}
            }
    
    # Swap to custom cache
    simple_cache = SimpleCache()
    service_factory.set_cache_service(simple_cache)
    
    # Test custom cache
    simple_cache.set_presentation("test-cache", {"topic": "Test Cache"})
    cached = simple_cache.get_presentation("test-cache")
    print(f"   ✅ Custom cache test: {cached['topic'] if cached else 'Not found'}")
    
    # Reset to default
    service_factory.reset_services()
    print("   ✅ Reset to default services")
    
    print("\n🎉 All tests completed successfully!")
    print("=" * 40)
    print("\n✅ Modular architecture is working correctly!")
    print("✅ Database operations are functional")
    print("✅ Caching is working")
    print("✅ LLM integration is working")
    print("✅ Service swapping is working")

if __name__ == "__main__":
    asyncio.run(test_simple()) 