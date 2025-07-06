from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import List
import uuid
from datetime import datetime
from app.models.presentation import Presentation, PresentationCreate, PresentationConfig
from app.services.slide_generator import SlideGenerator
from app.services.factory import service_factory
from app.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.themes import Theme, ThemeConfig

router = APIRouter()

cache_service = service_factory.get_cache_service()
storage = service_factory.get_storage_service()

def get_slide_generator():
    """Get a fresh slide generator with current LLM service"""
    llm_service = service_factory.get_llm_service()
    return SlideGenerator(cache_service, llm_service)

@router.post("/", response_model=Presentation)
async def create_presentation(
    presentation: PresentationCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new presentation"""
    try:
        presentation_id = str(uuid.uuid4())
        slide_generator = get_slide_generator()
        slides = await slide_generator.generate_slides(
            topic=presentation.topic,
            num_slides=presentation.num_slides,
            custom_content=presentation.custom_content
        )
        current_time = datetime.now().isoformat()
        new_presentation = Presentation(
            id=presentation_id,
            topic=presentation.topic,
            num_slides=presentation.num_slides,
            slides=slides,
            custom_content=presentation.custom_content,
            created_at=current_time,
            updated_at=current_time
        )
        success = await storage.save_presentation(session, new_presentation)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save presentation")
        return new_presentation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create presentation: {str(e)}")

@router.get("/", response_model=List[Presentation])
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

@router.get("/search/{topic}", response_model=List[Presentation])
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

@router.get("/{presentation_id}", response_model=Presentation)
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

@router.delete("/{presentation_id}")
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

@router.get("/{presentation_id}/download")
async def download_presentation(
    presentation_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Download presentation as PPTX"""
    try:
        presentation = await storage.get_presentation(session, presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        slide_generator = get_slide_generator()
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

@router.post("/{presentation_id}/configure", response_model=Presentation)
async def configure_presentation(
    presentation_id: str,
    config: PresentationConfig,
    session: AsyncSession = Depends(get_session)
):
    """Modify presentation configuration without regenerating content"""
    try:
        presentation = await storage.get_presentation(session, presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        # Only update the configuration properties
        if config.theme is not None:
            presentation.theme = config.theme
            # Set theme's default font and colors unless overridden by user
            if config.font is None:
                presentation.font = ThemeConfig.get_theme_font(config.theme)
            if config.colors is None:
                presentation.colors = ThemeConfig.get_theme_colors(config.theme)
        if config.font is not None:
            presentation.font = config.font
        if config.colors is not None:
            presentation.colors = config.colors
        if config.aspect_ratio is not None:
            presentation.aspect_ratio = config.aspect_ratio
        if config.custom_width is not None:
            presentation.custom_width = config.custom_width
        if config.custom_height is not None:
            presentation.custom_height = config.custom_height
        
        # Update timestamp
        presentation.updated_at = datetime.now().isoformat()
        
        # Save the updated presentation (no slide regeneration)
        success = await storage.save_presentation(session, presentation)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save updated presentation")
        
        # Clear cache to ensure we get fresh data from database
        cache_service.delete_presentation(presentation_id)
        
        # Get the updated presentation from database to ensure we return the latest values
        updated_presentation = await storage.get_presentation(session, presentation_id)
        if not updated_presentation:
            raise HTTPException(status_code=500, detail="Failed to retrieve updated presentation")
        
        return updated_presentation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to configure presentation: {str(e)}") 