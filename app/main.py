"""
Slide Generator API - Main Application
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import uuid
import os
from datetime import datetime
from app.settings import OPENAI_API_KEY

# Import our modules
from app.models.presentation import Presentation, PresentationCreate, PresentationConfig
from app.models.database import PresentationDB, SlideDB
from app.services.slide_generator import SlideGenerator
from app.services.factory import service_factory
from app.database import get_session, create_db_and_tables
from sqlalchemy.ext.asyncio import AsyncSession

# Import presentation endpoints from a new modular file
from app.presentation_api import router as presentation_router

# Import LLM implementations
from app.examples.openai_llm import OpenAILLM

app = FastAPI(
    title="Slide Generator API",
    description="Generate customizable presentation slides on any topic",
    version="1.0.0"
)

# Initialize services using factory
cache_service = service_factory.get_cache_service()
storage = service_factory.get_storage_service()


def configure_llm_service():
    """Configure LLM service based on settings file or environment variables"""
    if OPENAI_API_KEY:
        print("🔧 Using OpenAI LLM for content generation")
        openai_llm = OpenAILLM(api_key=OPENAI_API_KEY)
        service_factory.set_llm_service(openai_llm)
    else:
        print("🔧 Using Dummy LLM for content generation (set OPENAI_API_KEY to use OpenAI)")

# Configure LLM service
configure_llm_service()
llm_service = service_factory.get_llm_service()
slide_generator = SlideGenerator(cache_service, llm_service)

# Include presentation router
app.include_router(presentation_router, prefix="/api/v1/presentations")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await create_db_and_tables()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Slide Generator API is running"}

@app.get("/api/v1/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    return cache_service.get_cache_stats()

@app.post("/api/v1/cache/clear")
async def clear_cache():
    """Clear all caches"""
    cache_service.clear_all()
    return {"message": "All caches cleared"}

@app.get("/api/v1/llm/status")
async def get_llm_status():
    """Get current LLM service status"""
    current_llm = service_factory.get_llm_service()
    return {
        "llm_service": type(current_llm).__name__,
        "is_openai": isinstance(current_llm, OpenAILLM),
        "is_dummy": "DummyLLM" in type(current_llm).__name__
    }

@app.post("/api/v1/llm/switch")
async def switch_llm_service(llm_type: str = "dummy", api_key: Optional[str] = None):
    """Switch LLM service implementation"""
    try:
        if llm_type.lower() == "openai":
            if not api_key:
                raise HTTPException(status_code=400, detail="API key required for OpenAI")
            openai_llm = OpenAILLM(api_key=api_key)
            service_factory.set_llm_service(openai_llm)
            # Update the slide generator with new LLM service
            slide_generator = SlideGenerator(cache_service, service_factory.get_llm_service())
            return {"message": "Switched to OpenAI LLM", "llm_service": "OpenAILLM"}
        
        elif llm_type.lower() == "dummy":
            from app.services.dummy_llm import DummyLLM
            dummy_llm = DummyLLM()
            service_factory.set_llm_service(dummy_llm)
            # Update the slide generator with new LLM service
            slide_generator = SlideGenerator(cache_service, service_factory.get_llm_service())
            return {"message": "Switched to Dummy LLM", "llm_service": "DummyLLM"}
        
        else:
            raise HTTPException(status_code=400, detail="Invalid LLM type. Use 'openai' or 'dummy'")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to switch LLM service: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 