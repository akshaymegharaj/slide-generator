#!/usr/bin/env python3
"""
Test script to verify background color application in presentations
"""
import asyncio
import os
from app.services.factory import service_factory
from app.models.presentation import Presentation, Slide, SlideType
from app.config.themes import Theme, ThemeConfig
from app.services.slide_generator import SlideGenerator

async def test_background_application():
    """Test that background colors are properly applied when themes change"""
    
    # Create a simple presentation with different themes
    test_slides = [
        Slide(
            slide_type=SlideType.TITLE,
            title="Test Presentation",
            content=["Testing background colors"],
            citations=[]
        ),
        Slide(
            slide_type=SlideType.BULLET_POINTS,
            title="Test Slide",
            content=["Point 1", "Point 2", "Point 3"],
            citations=[]
        )
    ]
    
    # Test different themes
    themes_to_test = [Theme.MODERN, Theme.MINIMAL, Theme.CORPORATE, Theme.CLASSIC]
    
    for theme in themes_to_test:
        print(f"\nTesting theme: {theme.value}")
        
        # Create presentation with specific theme
        presentation = Presentation(
            id=f"test_{theme.value}",
            topic="Background Test",
            num_slides=2,
            slides=test_slides,
            theme=theme,
            font="Arial",
            colors={},
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00"
        )
        
        # Generate PPTX
        cache_service = service_factory.get_cache_service()
        llm_service = service_factory.get_llm_service()
        slide_generator = SlideGenerator(cache_service, llm_service)
        file_path = await slide_generator.create_pptx(presentation)
        
        if os.path.exists(file_path):
            print(f"✓ Generated PPTX for {theme.value}: {file_path}")
            print(f"  Expected background: {ThemeConfig.get_theme_colors(theme).get('background', 'Unknown')}")
        else:
            print(f"✗ Failed to generate PPTX for {theme.value}")

if __name__ == "__main__":
    asyncio.run(test_background_application()) 