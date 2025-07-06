"""
Slide Generator API - Main Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import uuid
import os

# Import our modules (we'll create these next)
from app.models.presentation import Presentation, PresentationCreate, PresentationConfig
from app.services.slide_generator import SlideGenerator
from app.services.storage import PresentationStorage

app = FastAPI(
    title="Slide Generator API",
    description="Generate customizable presentation slides on any topic",
    version="1.0.0"
)

# Initialize services
slide_generator = SlideGenerator()
storage = PresentationStorage()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Slide Generator API is running"}

@app.post("/api/v1/presentations", response_model=Presentation)
async def create_presentation(presentation: PresentationCreate):
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
        
        # Save to storage
        await storage.save_presentation(new_presentation)
        
        return new_presentation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create presentation: {str(e)}")

@app.get("/api/v1/presentations/{presentation_id}", response_model=Presentation)
async def get_presentation(presentation_id: str):
    """Retrieve presentation details"""
    try:
        presentation = await storage.get_presentation(presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        return presentation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve presentation: {str(e)}")

@app.get("/api/v1/presentations/{presentation_id}/download")
async def download_presentation(presentation_id: str):
    """Download presentation as PPTX"""
    try:
        presentation = await storage.get_presentation(presentation_id)
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
async def configure_presentation(presentation_id: str, config: PresentationConfig):
    """Modify presentation configuration"""
    try:
        presentation = await storage.get_presentation(presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        # Update configuration
        presentation.theme = config.theme
        presentation.font = config.font
        presentation.colors = config.colors
        
        # Regenerate slides with new configuration
        slides = await slide_generator.generate_slides(
            topic=presentation.topic,
            num_slides=presentation.num_slides,
            custom_content=presentation.custom_content,
            theme=config.theme,
            font=config.font,
            colors=config.colors
        )
        
        presentation.slides = slides
        
        # Save updated presentation
        await storage.save_presentation(presentation)
        
        return presentation
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to configure presentation: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 