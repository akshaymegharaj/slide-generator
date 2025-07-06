"""
Test script for the mature slide generator app with database and caching
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.database import create_db_and_tables, AsyncSessionLocal
from app.services.factory import service_factory
from app.services.slide_generator import SlideGenerator
from app.models.presentation import PresentationCreate, PresentationConfig, Theme

async def test_database_and_caching():
    """Test the database and caching functionality"""
    print("🧪 Testing Database and Caching Architecture")
    print("=" * 50)
    
    # Initialize database
    print("📊 Setting up database...")
    await create_db_and_tables()
    
    # Initialize services using factory
    print("⚡ Initializing services...")
    cache_service = service_factory.get_cache_service()
    storage = service_factory.get_storage_service()
    llm_service = service_factory.get_llm_service()
    slide_generator = SlideGenerator(cache_service, llm_service)
    
    # Test 1: Create a presentation
    print("\n1️⃣ Creating a presentation...")
    async with AsyncSessionLocal() as session:
        presentation_data = PresentationCreate(
            topic="Artificial Intelligence in Healthcare",
            num_slides=3,
            custom_content="Focus on practical applications and benefits"
        )
        
        # Generate slides
        slides = await slide_generator.generate_slides(
            topic=presentation_data.topic,
            num_slides=presentation_data.num_slides,
            custom_content=presentation_data.custom_content
        )
        
        # Create presentation object
        from app.models.presentation import Presentation
        presentation = Presentation(
            id="test-123",
            topic=presentation_data.topic,
            num_slides=presentation_data.num_slides,
            slides=slides,
            custom_content=presentation_data.custom_content
        )
        
        # Save to database
        success = await storage.save_presentation(session, presentation)
        print(f"   ✅ Presentation saved: {success}")
        
        # Test 2: Retrieve from cache first
        print("\n2️⃣ Testing cache retrieval...")
        cached_presentation = await storage.get_presentation(session, "test-123")
        if cached_presentation:
            print(f"   ✅ Retrieved from cache: {cached_presentation.topic}")
        
        # Test 3: Check cache stats
        print("\n3️⃣ Checking cache statistics...")
        cache_stats = cache_service.get_cache_stats()
        print(f"   📈 Presentation cache: {cache_stats['presentation_cache']['size']} items")
        print(f"   📈 Slide cache: {cache_stats['slide_cache']['size']} items")
        
        # Test 4: List presentations
        print("\n4️⃣ Listing presentations...")
        presentations = await storage.list_presentations(session)
        print(f"   📋 Found {len(presentations)} presentations")
        
        # Test 5: Search presentations
        print("\n5️⃣ Searching presentations...")
        search_results = await storage.search_presentations(session, "Healthcare")
        print(f"   🔍 Found {len(search_results)} presentations matching 'Healthcare'")
        
        # Test 6: Update presentation configuration
        print("\n6️⃣ Updating presentation configuration...")
        config = PresentationConfig(
            theme=Theme.CORPORATE,
            font="Times New Roman",
            colors={
                "primary": "#1f4e79",
                "secondary": "#2e8b57",
                "background": "#ffffff",
                "text": "#000000"
            }
        )
        
        # Update the presentation
        if config.theme is not None:
            presentation.theme = config.theme
        if config.font is not None:
            presentation.font = config.font
        if config.colors is not None:
            presentation.colors = config.colors
        
        # Regenerate slides with new config
        new_slides = await slide_generator.generate_slides(
            topic=presentation.topic,
            num_slides=presentation.num_slides,
            custom_content=presentation.custom_content,
            theme=config.theme or presentation.theme,
            font=config.font or presentation.font,
            colors=config.colors or presentation.colors
        )
        
        presentation.slides = new_slides
        success = await storage.save_presentation(session, presentation)
        print(f"   ✅ Configuration updated: {success}")
        
        # Test 7: Check updated cache stats
        print("\n7️⃣ Checking updated cache statistics...")
        updated_cache_stats = cache_service.get_cache_stats()
        print(f"   📈 Presentation cache: {updated_cache_stats['presentation_cache']['size']} items")
        print(f"   📈 Slide cache: {updated_cache_stats['slide_cache']['size']} items")
        
        # Test 8: Clear cache
        print("\n8️⃣ Testing cache clearing...")
        cache_service.clear_all()
        final_cache_stats = cache_service.get_cache_stats()
        print(f"   🧹 Cache cleared. Items remaining: {final_cache_stats['presentation_cache']['size']}")
        
        # Test 9: Delete presentation
        print("\n9️⃣ Deleting presentation...")
        success = await storage.delete_presentation(session, "test-123")
        print(f"   ✅ Presentation deleted: {success}")
    
    print("\n🎉 All tests completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_database_and_caching()) 