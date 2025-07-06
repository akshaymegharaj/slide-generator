#!/usr/bin/env python3
"""
Demo script to test the Slide Generator API
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api():
    """Test the complete API workflow"""
    print("🚀 Testing Slide Generator API")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Health Check")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: Create a presentation
    print("\n2. Creating Presentation")
    presentation_data = {
        "topic": "Machine Learning Fundamentals",
        "num_slides": 4,
        "custom_content": "Focus on supervised learning, neural networks, and practical applications"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/presentations", json=presentation_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        presentation = response.json()
        presentation_id = presentation["id"]
        print(f"Presentation ID: {presentation_id}")
        print(f"Topic: {presentation['topic']}")
        print(f"Number of slides: {presentation['num_slides']}")
        print(f"Slides created: {len(presentation['slides'])}")
        
        # Test 3: Retrieve the presentation
        print("\n3. Retrieving Presentation")
        response = requests.get(f"{BASE_URL}/api/v1/presentations/{presentation_id}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            retrieved = response.json()
            print(f"Retrieved successfully: {retrieved['topic']}")
        
        # Test 4: Configure the presentation
        print("\n4. Configuring Presentation")
        config_data = {
            "theme": "corporate",
            "font": "Calibri",
            "colors": {
                "primary": "#1f4e79",
                "secondary": "#4472c4",
                "background": "#ffffff",
                "text": "#2f2f2f"
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/presentations/{presentation_id}/configure", json=config_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            configured = response.json()
            print(f"Theme updated to: {configured['theme']}")
            print(f"Font updated to: {configured['font']}")
        
        # Test 5: Download the presentation
        print("\n5. Downloading Presentation")
        response = requests.get(f"{BASE_URL}/api/v1/presentations/{presentation_id}/download")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            filename = f"demo_presentation_{presentation_id[:8]}.pptx"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"Presentation downloaded as: {filename}")
        
        # Test 6: Create another presentation with different settings
        print("\n6. Creating Second Presentation")
        presentation_data_2 = {
            "topic": "Python Web Development",
            "num_slides": 2,
            "custom_content": "FastAPI, Django, and Flask comparison"
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/presentations", json=presentation_data_2)
        if response.status_code == 200:
            presentation_2 = response.json()
            print(f"Second presentation created: {presentation_2['topic']}")
            print(f"ID: {presentation_2['id']}")
    
    print("\n" + "=" * 50)
    print("✅ API Testing Complete!")
    print(f"📁 Check the 'output/' directory for generated PPTX files")
    print(f"📁 Check the 'storage/' directory for JSON data files")
    print(f"🌐 API Documentation: {BASE_URL}/docs")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("Make sure the server is running with: python -m app.main")
    except Exception as e:
        print(f"❌ Error: {e}") 