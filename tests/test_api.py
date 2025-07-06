import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 1. Health check

def test_health_check():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["message"].lower().startswith("slide generator api")

# 2. Create presentation

def test_create_presentation():
    data = {
        "topic": "Test Topic",
        "num_slides": 3,
        "custom_content": "Test content"
    }
    resp = client.post("/api/v1/presentations", json=data)
    assert resp.status_code == 200
    body = resp.json()
    assert body["topic"] == data["topic"]
    assert body["num_slides"] == data["num_slides"]
    assert len(body["slides"]) == data["num_slides"]
    global PRES_ID
    PRES_ID = body["id"]

# 3. Get presentation by ID

def test_get_presentation():
    resp = client.get(f"/api/v1/presentations/{PRES_ID}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == PRES_ID

# 4. Configure presentation (theme/aspect ratio)

def test_configure_presentation():
    config = {
        "theme": "minimal",
        "aspect_ratio": "4:3"
    }
    resp = client.post(f"/api/v1/presentations/{PRES_ID}/configure", json=config)
    assert resp.status_code == 200
    body = resp.json()
    assert body["theme"] == "minimal"
    assert body["aspect_ratio"] == "4:3"

# 5. Download PPTX

def test_download_pptx():
    resp = client.get(f"/api/v1/presentations/{PRES_ID}/download")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/vnd.openxmlformats-officedocument.presentationml.presentation")

# 6. Delete presentation

def test_delete_presentation():
    resp = client.delete(f"/api/v1/presentations/{PRES_ID}")
    assert resp.status_code == 200
    assert "deleted" in resp.json()["message"].lower()

# 7. Cache clear endpoint

def test_cache_clear():
    resp = client.post("/api/v1/cache/clear")
    assert resp.status_code == 200
    assert "cleared" in resp.json()["message"].lower() 