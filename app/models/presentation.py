"""
Presentation models for the Slide Generator API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from app.config.themes import Theme, ThemeConfig

class SlideType(str, Enum):
    """Types of slides supported"""
    TITLE = "title"
    BULLET_POINTS = "bullet_points"
    TWO_COLUMN = "two_column"
    CONTENT_WITH_IMAGE = "content_with_image"

class Slide(BaseModel):
    """Individual slide model"""
    slide_type: SlideType
    title: str
    content: List[str] = Field(default_factory=list)
    image_suggestion: Optional[str] = None
    citations: List[str] = Field(default_factory=list)

class PresentationCreate(BaseModel):
    """Model for creating a new presentation"""
    topic: str = Field(..., min_length=1, max_length=200, description="The topic/subject for the presentation")
    num_slides: int = Field(..., ge=1, le=20, description="Number of slides (1-20)")
    custom_content: Optional[str] = Field(None, max_length=2000, description="Custom content to include")

class PresentationConfig(BaseModel):
    """Model for presentation configuration"""
    theme: Optional[Theme] = Field(Theme.MODERN, description="Presentation theme")
    font: Optional[str] = Field(ThemeConfig.get_theme_font(Theme.MODERN), description="Font family")
    colors: Optional[Dict[str, str]] = Field(
        default_factory=lambda: ThemeConfig.get_theme_colors(Theme.MODERN),
        description="Color scheme"
    )

class Presentation(BaseModel):
    """Complete presentation model"""
    id: str
    topic: str
    num_slides: int
    slides: List[Slide] = Field(default_factory=list)
    custom_content: Optional[str] = None
    theme: Theme = Theme.MODERN
    font: str = ThemeConfig.get_theme_font(Theme.MODERN)
    colors: Dict[str, str] = Field(
        default_factory=lambda: ThemeConfig.get_theme_colors(Theme.MODERN)
    )
    created_at: Optional[str] = None
    updated_at: Optional[str] = None 