"""
Presentation models for the Slide Generator API
"""
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict, Any
from enum import Enum
from app.config.themes import Theme, ThemeConfig
from app.config.aspect_ratios import AspectRatio, AspectRatioConfig

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
    theme: Optional[Theme] = Field(Theme.MODERN, description="Presentation theme")
    font: Optional[str] = Field(None, description="Font family (will use theme default if not specified)")
    colors: Optional[Dict[str, str]] = Field(None, description="Color scheme (will use theme default if not specified)")
    aspect_ratio: Optional[AspectRatio] = Field(AspectRatio.WIDESCREEN_16_9, description="Presentation aspect ratio")
    custom_width: Optional[float] = Field(None, ge=5.0, le=20.0, description="Custom width in inches (for custom aspect ratio)")
    custom_height: Optional[float] = Field(None, ge=5.0, le=20.0, description="Custom height in inches (for custom aspect ratio)")

class PresentationConfig(BaseModel):
    """Model for presentation configuration"""
    theme: Optional[Theme] = Field(Theme.MODERN, description="Presentation theme")
    font: Optional[str] = Field(None, description="Font family (derived from theme if not specified)")
    colors: Optional[Dict[str, str]] = Field(None, description="Color scheme (derived from theme if not specified)")
    aspect_ratio: Optional[AspectRatio] = Field(AspectRatio.WIDESCREEN_16_9, description="Presentation aspect ratio")
    custom_width: Optional[float] = Field(None, ge=5.0, le=20.0, description="Custom width in inches (for custom aspect ratio)")
    custom_height: Optional[float] = Field(None, ge=5.0, le=20.0, description="Custom height in inches (for custom aspect ratio)")
    
    @model_validator(mode='after')
    def set_theme_defaults(self):
        """Set font and colors based on theme if not explicitly provided"""
        if self.theme:
            if self.font is None:
                self.font = ThemeConfig.get_theme_font(self.theme)
            if self.colors is None:
                self.colors = ThemeConfig.get_theme_colors(self.theme)
        return self

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
    aspect_ratio: AspectRatio = AspectRatio.WIDESCREEN_16_9
    custom_width: Optional[float] = None
    custom_height: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None 