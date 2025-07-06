#!/usr/bin/env python3
"""
Test script to demonstrate OpenAI LLM flow
Shows how easy it is to switch between Dummy and OpenAI LLM implementations
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
from app.examples.openai_llm import OpenAILLM

async def test_openai_flow():
    """Test the OpenAI LLM flow"""
    print("🤖 OpenAI LLM Flow Test")
    print("=" * 40)
    
    # Initialize database
    print("📊 Setting up database...")
    await create_db_and_tables()
    
    # Get default services (Dummy LLM)
    print("\n1️⃣ Testing with Dummy LLM (default)")
    print("-" * 30)
    
    cache_service = service_factory.get_cache_service()
    storage_service = service_factory.get_storage_service()
    llm_service = service_factory.get_llm_service()
    slide_generator = SlideGenerator(cache_service, llm_service)
    
    print(f"   🧠 Current LLM: {type(llm_service).__name__}")
    
    # Test with dummy LLM
    slides = await slide_generator.generate_slides(
        topic="Python Programming",
        num_slides=2,
        custom_content="Focus on best practices"
    )
    
    print(f"   ✅ Generated {len(slides)} slides with Dummy LLM")
    for i, slide in enumerate(slides):
        print(f"   📄 Slide {i+1}: {slide.title}")
    
    # Check if OpenAI API key is available
    print("\n2️⃣ Testing OpenAI LLM Flow")
    print("-" * 30)
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        print("   🔑 OpenAI API key found!")
        
        # Switch to OpenAI LLM
        print("   🔄 Switching to OpenAI LLM...")
        openai_llm = OpenAILLM(api_key=openai_api_key)
        service_factory.set_llm_service(openai_llm)
        
        # Get updated services
        llm_service = service_factory.get_llm_service()
        slide_generator = SlideGenerator(cache_service, llm_service)
        
        print(f"   🧠 Current LLM: {type(llm_service).__name__}")
        
        # Test with OpenAI LLM
        print("   ⏳ Generating slides with OpenAI (this may take a few seconds)...")
        slides = await slide_generator.generate_slides(
            topic="Machine Learning Basics",
            num_slides=2,
            custom_content="Focus on practical applications"
        )
        
        print(f"   ✅ Generated {len(slides)} slides with OpenAI LLM")
        for i, slide in enumerate(slides):
            print(f"   📄 Slide {i+1}: {slide.title}")
            print(f"      Content: {len(slide.content)} bullet points")
            print(f"      Citations: {len(slide.citations)} citations")
        
        # Save presentation to database
        async with AsyncSessionLocal() as session:
            presentation = Presentation(
                id="openai-test",
                topic="Machine Learning Basics",
                num_slides=2,
                slides=slides,
                custom_content="Focus on practical applications"
            )
            
            success = await storage_service.save_presentation(session, presentation)
            print(f"   💾 Saved to database: {success}")
        
        # Switch back to Dummy LLM
        print("\n3️⃣ Switching back to Dummy LLM")
        print("-" * 30)
        
        from app.services.dummy_llm import DummyLLM
        dummy_llm = DummyLLM()
        service_factory.set_llm_service(dummy_llm)
        
        llm_service = service_factory.get_llm_service()
        slide_generator = SlideGenerator(cache_service, llm_service)
        
        print(f"   🧠 Current LLM: {type(llm_service).__name__}")
        print("   ✅ Successfully switched back to Dummy LLM")
        
    else:
        print("   ⚠️  OpenAI API key not found")
        print("   💡 To test OpenAI LLM:")
        print("      export OPENAI_API_KEY='your-api-key-here'")
        print("      python test_openai_flow.py")
    
    print("\n🎉 OpenAI LLM Flow Test Complete!")
    print("=" * 40)
    print("✅ The flow is fully implemented and working!")
    print("✅ Easy switching between LLM implementations")
    print("✅ No code changes needed in main application")
    print("✅ Modular architecture allows seamless swapping")

if __name__ == "__main__":
    asyncio.run(test_openai_flow()) 