"""
Database models using SQLModel for the Slide Generator API
"""
from sqlmodel import SQLModel, Field, JSON, Column
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class SlideType(str, Enum):
    """Types of slides supported"""
    TITLE = "title"
    BULLET_POINTS = "bullet_points"
    TWO_COLUMN = "two_column"
    CONTENT_WITH_IMAGE = "content_with_image"

class Theme(str, Enum):
    """Available themes"""
    MODERN = "modern"
    CLASSIC = "classic"
    MINIMAL = "minimal"
    CORPORATE = "corporate"

class SlideDB(SQLModel, table=True):
    """Database model for individual slides"""
    __tablename__ = "slides"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    presentation_id: str = Field(foreign_key="presentations.id")
    slide_type: SlideType
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
    theme: Theme = Field(default=Theme.MODERN)
    font: str = Field(default="Arial")
    colors: Dict[str, str] = Field(
        sa_column=Column(JSON),
        default_factory=lambda: {
            "primary": "#2E86AB",
            "secondary": "#A23B72",
            "background": "#FFFFFF",
            "text": "#000000"
        }
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow) 