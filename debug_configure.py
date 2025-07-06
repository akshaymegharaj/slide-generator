#!/usr/bin/env python3
"""
Debug script to test the configure endpoint
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.config.aspect_ratios import AspectRatio

client = TestClient(app)
client.headers = {"X-API-Key": "test-api-key"}

def test_configure():
    # First create a presentation
    create_data = {
        "topic": "Test Topic",
        "num_slides": 3,
        "custom_content": "Test content"
    }
    resp = client.post("/api/v1/presentations", json=create_data)
    print(f"Create response status: {resp.status_code}")
    if resp.status_code == 200:
        presentation = resp.json()
        presentation_id = presentation["id"]
        print(f"Created presentation ID: {presentation_id}")
        print(f"Initial aspect ratio: {presentation['aspect_ratio']}")
        
        # Now configure it
        config = {
            "theme": "minimal",
            "aspect_ratio": "4:3"
        }
        print(f"Configuring with: {config}")
        resp = client.post(f"/api/v1/presentations/{presentation_id}/configure", json=config)
        print(f"Configure response status: {resp.status_code}")
        if resp.status_code == 200:
            updated = resp.json()
            print(f"Updated aspect ratio: {updated['aspect_ratio']}")
            print(f"Updated theme: {updated['theme']}")
        else:
            print(f"Configure error: {resp.text}")
    else:
        print(f"Create error: {resp.text}")

if __name__ == "__main__":
    test_configure() 