"""
Slide Generator API - Main Application
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import uuid
import os

# Import our modules
from app.models.presentation import Presentation, PresentationCreate, PresentationConfig
from app.models.database import PresentationDB, SlideDB
from app.services.slide_generator import SlideGenerator
from app.services.factory import service_factory
from app.database import get_session, create_db_and_tables
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(
    title="Slide Generator API",
    description="Generate customizable presentation slides on any topic",
    version="1.0.0"
)

# Initialize services using factory
cache_service = service_factory.get_cache_service()
storage = service_factory.get_storage_service()
llm_service = service_factory.get_llm_service()
slide_generator = SlideGenerator(cache_service, llm_service)

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

@app.post("/api/v1/presentations", response_model=Presentation)
async def create_presentation(
    presentation: PresentationCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new presentation"""
    try:
        # Generate unique ID
        presentation_id = str(uuid.uuid4())
        
        # Generate slides
        slides = await slide_generator.generate_slides(
            topic=presentation.topic,
            num_slides=presentation.num_slides,
            custom_content=presentation.custom_content
        )
        
        # Create presentation object
        new_presentation = Presentation(
            id=presentation_id,
            topic=presentation.topic,
            num_slides=presentation.num_slides,
            slides=slides,
            custom_content=presentation.custom_content
        )
        
        # Save to database
        success = await storage.save_presentation(session, new_presentation)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save presentation")
        
        return new_presentation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create presentation: {str(e)}")

@app.get("/api/v1/presentations", response_model=List[Presentation])
async def list_presentations(
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session)
):
    """List all presentations"""
    try:
        presentations = await storage.list_presentations(session, limit=limit, offset=offset)
        return presentations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list presentations: {str(e)}")

@app.get("/api/v1/presentations/search/{topic}", response_model=List[Presentation])
async def search_presentations(
    topic: str,
    session: AsyncSession = Depends(get_session)
):
    """Search presentations by topic"""
    try:
        presentations = await storage.search_presentations(session, topic)
        return presentations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search presentations: {str(e)}")

@app.get("/api/v1/presentations/{presentation_id}", response_model=Presentation)
async def get_presentation(
    presentation_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Retrieve presentation details"""
    try:
        presentation = await storage.get_presentation(session, presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        return presentation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve presentation: {str(e)}")

@app.delete("/api/v1/presentations/{presentation_id}")
async def delete_presentation(
    presentation_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Delete a presentation"""
    try:
        success = await storage.delete_presentation(session, presentation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Presentation not found")
        return {"message": "Presentation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete presentation: {str(e)}")

@app.get("/api/v1/presentations/{presentation_id}/download")
async def download_presentation(
    presentation_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Download presentation as PPTX"""
    try:
        presentation = await storage.get_presentation(session, presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        # Generate PPTX file
        file_path = await slide_generator.create_pptx(presentation)
        
        return FileResponse(
            path=file_path,
            filename=f"presentation_{presentation_id}.pptx",
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download presentation: {str(e)}")

@app.post("/api/v1/presentations/{presentation_id}/configure", response_model=Presentation)
async def configure_presentation(
    presentation_id: str,
    config: PresentationConfig,
    session: AsyncSession = Depends(get_session)
):
    """Modify presentation configuration"""
    try:
        presentation = await storage.get_presentation(session, presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        # Update configuration
        if config.theme is not None:
            presentation.theme = config.theme
        if config.font is not None:
            presentation.font = config.font
        if config.colors is not None:
            presentation.colors = config.colors
        
        # Regenerate slides with new configuration
        slides = await slide_generator.generate_slides(
            topic=presentation.topic,
            num_slides=presentation.num_slides,
            custom_content=presentation.custom_content,
            theme=config.theme or presentation.theme,
            font=config.font or presentation.font,
            colors=config.colors or presentation.colors
        )
        
        presentation.slides = slides
        
        # Save updated presentation
        success = await storage.save_presentation(session, presentation)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save updated presentation")
        
        return presentation
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to configure presentation: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 