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
from app.models.presentation import AspectRatio

router = APIRouter()

cache_service = service_factory.get_cache_service()
storage = service_factory.get_storage_service()

def get_slide_generator():
    """Get a fresh slide generator with current LLM service"""
    llm_service = service_factory.get_llm_service()
    return SlideGenerator(cache_service, llm_service)

# Utility to apply theme defaults

def apply_theme_defaults(presentation, theme, font=None, colors=None):
    """Set font and colors to theme defaults unless overridden"""
    # If theme is being changed, apply theme defaults for font and colors
    if theme is not None and theme != presentation.theme:
        presentation.theme = theme
        # Only override font/colors if they weren't explicitly provided
        if font is None:
            presentation.font = ThemeConfig.get_theme_font(theme)
        else:
            presentation.font = font
        if colors is None:
            presentation.colors = ThemeConfig.get_theme_colors(theme)
        else:
            presentation.colors = colors
    else:
        # If theme is not changing, only update what's explicitly provided
        if theme is not None:
            presentation.theme = theme
        if font is not None:
            presentation.font = font
        if colors is not None:
            presentation.colors = colors
    return presentation

@router.post("/", response_model=Presentation, tags=["Presentation"])
async def create_presentation(
    presentation: PresentationCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new presentation"""
    # Validate number of slides
    if presentation.num_slides < 1 or presentation.num_slides > 20:
        raise HTTPException(
            status_code=400, 
            detail="Number of slides must be between 1 and 20"
        )
    
    try:
        presentation_id = str(uuid.uuid4())
        slide_generator = get_slide_generator()
        slides = await slide_generator.generate_slides(
            topic=presentation.topic,
            num_slides=presentation.num_slides,
            custom_content=presentation.custom_content
        )
        current_time = datetime.now().isoformat()
        
        # Create new presentation with user-specified theme, font, and colors
        new_presentation = Presentation(
            id=presentation_id,
            topic=presentation.topic,
            num_slides=presentation.num_slides,
            slides=slides,
            custom_content=presentation.custom_content,
            theme=presentation.theme or Theme.MODERN,
            font=presentation.font or ThemeConfig.get_theme_font(presentation.theme or Theme.MODERN),
            colors=presentation.colors or ThemeConfig.get_theme_colors(presentation.theme or Theme.MODERN),
            aspect_ratio=presentation.aspect_ratio or AspectRatio.WIDESCREEN_16_9,
            custom_width=presentation.custom_width,
            custom_height=presentation.custom_height,
            created_at=current_time,
            updated_at=current_time
        )
        
        # Apply theme defaults to ensure font and colors are set correctly
        apply_theme_defaults(
            new_presentation,
            presentation.theme,
            presentation.font,
            presentation.colors
        )
        
        success = await storage.save_presentation(session, new_presentation)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save presentation")
        return new_presentation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create presentation: {str(e)}")

@router.get("/", response_model=List[Presentation], tags=["Presentation"])
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

@router.get("/search/{topic}", response_model=List[Presentation], tags=["Presentation"])
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

@router.get("/{presentation_id}", response_model=Presentation, tags=["Presentation"])
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

@router.delete("/{presentation_id}", tags=["Presentation"])
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

@router.get("/{presentation_id}/download", tags=["Presentation"])
async def download_presentation(
    presentation_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Download presentation as PPTX with latest theme, color, and font values"""
    try:
        # Clear cache to ensure we get fresh data from database
        cache_service.delete_presentation(presentation_id)
        
        # Fetch fresh presentation data directly from database
        presentation = await storage.get_presentation(session, presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        # Ensure latest theme configuration is applied
        # If theme is set, ensure font and colors are up to date
        if presentation.theme:
            # Update font if not set or if it's the default theme font
            if not presentation.font or presentation.font == ThemeConfig.get_theme_font(Theme.MODERN):
                presentation.font = ThemeConfig.get_theme_font(presentation.theme)
            
            # Update colors if not set or if they're the default theme colors
            if not presentation.colors or presentation.colors == ThemeConfig.get_theme_colors(Theme.MODERN):
                presentation.colors = ThemeConfig.get_theme_colors(presentation.theme)
        
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

@router.post("/{presentation_id}/configure", response_model=Presentation, tags=["Presentation"])
async def configure_presentation(
    presentation_id: str,
    config: PresentationConfig,
    session: AsyncSession = Depends(get_session)
):
    """
    Modify presentation configuration without regenerating content.
    You can update theme, font, colors, aspect_ratio, custom_width, and custom_height here.
    """
    try:
        # Clear cache first to ensure we get fresh data
        cache_service.delete_presentation(presentation_id)
        
        presentation = await storage.get_presentation(session, presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        # Apply theme changes first
        if config.theme is not None:
            presentation.theme = config.theme
            # If theme is changing, apply theme defaults for font and colors unless overridden
            if config.font is None:
                presentation.font = ThemeConfig.get_theme_font(config.theme)
            if config.colors is None:
                presentation.colors = ThemeConfig.get_theme_colors(config.theme)
        
        # Apply individual overrides
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
        
        # Save the updated presentation
        success = await storage.save_presentation(session, presentation)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save updated presentation")
        
        # Clear cache again and get fresh data
        cache_service.delete_presentation(presentation_id)
        updated_presentation = await storage.get_presentation(session, presentation_id)
        if not updated_presentation:
            raise HTTPException(status_code=500, detail="Failed to retrieve updated presentation")
        
        return updated_presentation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to configure presentation: {str(e)}") 