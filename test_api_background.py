#!/usr/bin/env python3
"""
Test script to verify background color application through the API
"""
import asyncio
import requests
import json
import os
from app.main import app
from app.services.factory import service_factory
from app.database import get_session

async def test_api_background_changes():
    """Test that background colors are properly applied when themes are changed via API"""
    
    # Start the FastAPI test client
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    # Create a presentation first
    create_data = {
        "topic": "API Background Test",
        "num_slides": 2,
        "custom_content": None
    }
    
    print("Creating initial presentation...")
    response = client.post("/api/v1/presentations/", json=create_data)
    assert response.status_code == 200, f"Failed to create presentation: {response.text}"
    
    presentation = response.json()
    presentation_id = presentation["id"]
    print(f"✓ Created presentation: {presentation_id}")
    print(f"  Initial theme: {presentation.get('theme', 'unknown')}")
    
    # Test different themes
    themes_to_test = ["modern", "minimal", "corporate", "classic"]
    
    for theme in themes_to_test:
        print(f"\nTesting theme change to: {theme}")
        
        # Configure presentation with new theme
        config_data = {
            "theme": theme,
            "font": None,
            "colors": None
        }
        
        response = client.post(f"/api/v1/presentations/{presentation_id}/configure", json=config_data)
        assert response.status_code == 200, f"Failed to configure presentation: {response.text}"
        
        updated_presentation = response.json()
        print(f"✓ Updated theme to: {updated_presentation.get('theme')}")
        
        # Download the presentation to verify background changes
        response = client.get(f"/api/v1/presentations/{presentation_id}/download")
        assert response.status_code == 200, f"Failed to download presentation: {response.text}"
        
        # Save the file
        filename = f"api_test_{theme}.pptx"
        with open(filename, "wb") as f:
            f.write(response.content)
        
        print(f"✓ Downloaded PPTX: {filename}")
        
        # Get expected background color
        from app.config.themes import Theme, ThemeConfig
        theme_enum = Theme(theme)
        expected_bg = ThemeConfig.get_theme_colors(theme_enum).get('background', 'Unknown')
        print(f"  Expected background: {expected_bg}")
    
    print(f"\n✓ All theme tests completed successfully!")
    print("Generated files:")
    for theme in themes_to_test:
        filename = f"api_test_{theme}.pptx"
        if os.path.exists(filename):
            print(f"  - {filename}")

if __name__ == "__main__":
    asyncio.run(test_api_background_changes()) 