#!/usr/bin/env python3
"""
Script to check citations in presentations
"""
import asyncio
import json
import os
from app.models.presentation import PresentationCreate
from app.services.factory import service_factory
from app.services.slide_generator import SlideGenerator

async def check_citations_in_slides():
    """Check citations in generated slides"""
    print('📚 Checking Citations in Generated Slides')
    print('=' * 50)
    
    # Get services
    cache_service = service_factory.get_cache_service()
    llm_service = service_factory.get_llm_service()
    slide_generator = SlideGenerator(cache_service, llm_service)
    
    # Generate slides
    slides = await slide_generator.generate_slides(
        topic='Machine Learning Basics',
        num_slides=3,
        custom_content='Focus on practical applications'
    )
    
    print(f'Generated {len(slides)} slides')
    
    total_citations = 0
    
    # Check citations in each slide
    for i, slide in enumerate(slides):
        print(f'\nSlide {i+1}: {slide.slide_type.value}')
        print(f'  Title: {slide.title}')
        print(f'  Citations: {len(slide.citations)}')
        
        if slide.citations:
            for j, citation in enumerate(slide.citations):
                print(f'    {j+1}. {citation}')
            total_citations += len(slide.citations)
        else:
            print('    No citations')
    
    print(f'\n📊 Summary:')
    print(f'  Total slides: {len(slides)}')
    print(f'  Total citations: {total_citations}')
    print(f'  Average citations per slide: {total_citations/len(slides):.1f}')
    
    return slides

async def check_citations_from_api():
    """Check citations by making API calls"""
    import requests
    
    BASE_URL = 'http://localhost:8000'
    
    print('\n🌐 Checking Citations via API')
    print('=' * 40)
    
    # Create a presentation
    create_data = {
        'topic': 'API Citation Test',
        'num_slides': 3,
        'custom_content': 'Test citations'
    }
    
    response = requests.post(f'{BASE_URL}/api/v1/presentations', json=create_data)
    
    if response.status_code == 200:
        presentation = response.json()
        presentation_id = presentation['id']
        print(f'✅ Created presentation: {presentation_id}')
        
        # Check citations in the response
        total_citations = 0
        for i, slide in enumerate(presentation['slides']):
            citations = slide.get('citations', [])
            print(f'\nSlide {i+1}: {slide["slide_type"]}')
            print(f'  Title: {slide["title"]}')
            print(f'  Citations: {len(citations)}')
            
            for j, citation in enumerate(citations):
                print(f'    {j+1}. {citation}')
            total_citations += len(citations)
        
        print(f'\n📊 API Summary:')
        print(f'  Total slides: {len(presentation["slides"])}')
        print(f'  Total citations: {total_citations}')
        
        return presentation_id
    else:
        print(f'❌ Failed to create presentation: {response.status_code}')
        return None

def check_citation_implementation():
    """Check how citations are implemented in the code"""
    print('\n🔍 Citation Implementation Analysis')
    print('=' * 40)
    
    print('1. Citation Generation:')
    print('   - Dummy LLM generates 2 citations per slide')
    print('   - Citations are topic-specific')
    print('   - Format: "Research paper on {topic}", "Industry report on {topic}"')
    
    print('\n2. Citation Storage:')
    print('   - Citations stored in Slide model')
    print('   - Saved to database with presentations')
    print('   - Cached with slide generation results')
    
    print('\n3. Citation in PPTX:')
    print('   - Currently NOT added to PPTX slides')
    print('   - Citations are in slide data but not rendered')
    print('   - Need to implement citation display in slide creation methods')

async def main():
    """Main function to check citations"""
    print('📚 Citation Check Tool')
    print('=' * 60)
    
    # Check citations in generated slides
    await check_citations_in_slides()
    
    # Check citations via API
    await check_citations_from_api()
    
    # Check implementation
    check_citation_implementation()
    
    print('\n💡 To add citations to PPTX slides:')
    print('1. Modify slide creation methods in slide_generator.py')
    print('2. Add citation text boxes to slides')
    print('3. Position citations at bottom of slides')
    print('4. Apply appropriate styling to citations')

if __name__ == "__main__":
    asyncio.run(main()) 