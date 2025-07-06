"""
Database models using SQLModel for the Slide Generator API
"""
from sqlmodel import SQLModel, Field, JSON, Column
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from app.config.themes import Theme, ThemeConfig
from app.config.aspect_ratios import AspectRatio, AspectRatioConfig

class SlideType(str, Enum):
    """Types of slides supported"""
    TITLE = "title"
    BULLET_POINTS = "bullet_points"
    TWO_COLUMN = "two_column"
    CONTENT_WITH_IMAGE = "content_with_image"

class SlideDB(SQLModel, table=True):
    """Database model for individual slides"""
    __tablename__ = "slides"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    presentation_id: str = Field(foreign_key="presentations.id")
    slide_type: str
    title: str
    content: List[str] = Field(sa_column=Column(JSON))
    image_suggestion: Optional[str] = None
    citations: List[str] = Field(sa_column=Column(JSON), default_factory=list)
    slide_order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PresentationDB(SQLModel, table=True):
    """Database model for presentations"""
    __tablename__ = "presentations"
    
    id: str = Field(primary_key=True)
    topic: str = Field(max_length=200)
    num_slides: int = Field(ge=1, le=20)
    custom_content: Optional[str] = Field(max_length=2000, default=None)
    theme: str = Field(default=Theme.MODERN.value)
    font: str = Field(default=ThemeConfig.get_theme_font(Theme.MODERN))
    colors: Dict[str, str] = Field(
        sa_column=Column(JSON),
        default_factory=lambda: ThemeConfig.get_theme_colors(Theme.MODERN)
    )
    aspect_ratio: str = Field(default=AspectRatio.WIDESCREEN_16_9.value)
    custom_width: Optional[float] = Field(default=None, ge=5.0, le=20.0)
    custom_height: Optional[float] = Field(default=None, ge=5.0, le=20.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow) 