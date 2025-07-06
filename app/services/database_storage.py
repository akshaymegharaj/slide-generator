"""
Database-based storage service using SQLModel
"""
from sqlmodel import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import text
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.database import PresentationDB, SlideDB, SlideType as DBSlideType, Theme as DBTheme
from app.models.presentation import Presentation, Slide, PresentationCreate, PresentationConfig, SlideType
from app.config.themes import Theme
from app.config.aspect_ratios import AspectRatio
from app.interfaces.storage import StorageInterface
from app.interfaces.cache import CacheInterface

# Helper to get enum value or string
def get_enum_value(val):
    return val.value if hasattr(val, 'value') else val

def safe_enum_conversion(enum_class, value):
    """Safely convert string values to enum, handling legacy data"""
    if isinstance(value, enum_class):
        return value
    
    if not value:
        # Return first enum value as default
        return list(enum_class)[0]
    
    # Handle legacy enum names that might be stored in the database
    legacy_mappings = {
        # AspectRatio legacy mappings
        'WIDESCREEN_16_9': '16:9',
        'STANDARD_4_3': '4:3',
        'CUSTOM': 'custom',
        # SlideType legacy mappings  
        'TITLE': 'title',
        'CONTENT': 'content',
        'IMAGE': 'image',
        'QUOTE': 'quote',
        'CHART': 'chart',
        'COMPARISON': 'comparison',
        'TIMELINE': 'timeline',
        'PROCESS': 'process',
        'SUMMARY': 'summary'
    }
    
    # Check if it's a legacy enum name
    if value in legacy_mappings:
        value = legacy_mappings[value]
    
    try:
        return enum_class(value)
    except ValueError:
        print(f"Warning: Invalid {enum_class.__name__} value '{value}', using default")
        # Return first enum value as default
        return list(enum_class)[0]

class DatabaseStorage(StorageInterface):
    """Database-based storage service with caching"""
    
    def __init__(self, cache_service: CacheInterface):
        self.cache = cache_service
    
    async def save_presentation(self, session: AsyncSession, presentation: Presentation) -> bool:
        """Save a presentation to database"""
        try:
            # Check if presentation exists
            existing_statement = select(PresentationDB).where(PresentationDB.id == presentation.id)
            existing_result = await session.execute(existing_statement)
            existing_presentation = existing_result.scalar_one_or_none()
            
            aspect_ratio_value = get_enum_value(presentation.aspect_ratio)
            
            if existing_presentation:
                # Update existing presentation
                existing_presentation.topic = presentation.topic
                existing_presentation.num_slides = presentation.num_slides
                existing_presentation.custom_content = presentation.custom_content
                existing_presentation.theme = get_enum_value(presentation.theme)
                existing_presentation.font = presentation.font
                existing_presentation.colors = presentation.colors
                existing_presentation.aspect_ratio = aspect_ratio_value
                existing_presentation.custom_width = presentation.custom_width
                existing_presentation.custom_height = presentation.custom_height
                existing_presentation.updated_at = datetime.utcnow()
                await session.flush()  # Ensure changes are flushed before slide operations
            else:
                # Create new presentation
                created_at = datetime.utcnow()
                if presentation.created_at:
                    try:
                        if isinstance(presentation.created_at, str):
                            created_at = datetime.fromisoformat(presentation.created_at.replace('Z', '+00:00'))
                        else:
                            created_at = presentation.created_at
                    except:
                        created_at = datetime.utcnow()
                
                presentation_db = PresentationDB(
                    id=presentation.id,
                    topic=presentation.topic,
                    num_slides=presentation.num_slides,
                    custom_content=presentation.custom_content,
                    theme=get_enum_value(presentation.theme),
                    font=presentation.font,
                    colors=presentation.colors,
                    aspect_ratio=aspect_ratio_value,
                    custom_width=presentation.custom_width,
                    custom_height=presentation.custom_height,
                    created_at=created_at,
                    updated_at=datetime.utcnow()
                )
                session.add(presentation_db)
                await session.flush()
            
            # Delete existing slides for this presentation
            await session.execute(
                delete(SlideDB).where(SlideDB.presentation_id == presentation.id)
            )
            
            # Add slides
            for i, slide in enumerate(presentation.slides):
                slide_db = SlideDB(
                    presentation_id=presentation.id,
                    slide_type=get_enum_value(slide.slide_type),
                    title=slide.title,
                    content=slide.content,
                    image_suggestion=slide.image_suggestion,
                    citations=slide.citations,
                    slide_order=i
                )
                session.add(slide_db)
            
            await session.commit()
            
            # Get the saved presentation with proper timestamps
            saved_presentation = await self.get_presentation(session, presentation.id)
            if saved_presentation:
                # Update cache with the saved presentation (which has timestamps)
                self.cache.set_presentation(presentation.id, saved_presentation.model_dump())
            
            return True
            
        except Exception as e:
            await session.rollback()
            print(f"Error saving presentation to database: {e}")
            return False
    
    async def get_presentation(self, session: AsyncSession, presentation_id: str) -> Optional[Presentation]:
        """Retrieve a presentation from database with caching"""
        try:
            # Check cache first
            cached = self.cache.get_presentation(presentation_id)
            if cached:
                return Presentation(**cached)
            
            # Query database
            statement = select(PresentationDB).where(PresentationDB.id == presentation_id)
            result = await session.execute(statement)
            presentation_db = result.scalar_one_or_none()
            
            if not presentation_db:
                return None
            
            # Get slides for this presentation
            slides_statement = select(SlideDB).where(
                SlideDB.presentation_id == presentation_id
            ).order_by(SlideDB.slide_order.asc())
            
            slides_result = await session.execute(slides_statement)
            slides_db = slides_result.scalars().all()
            
            # Convert to domain models with safe enum conversion
            slides = [
                Slide(
                    slide_type=safe_enum_conversion(SlideType, slide.slide_type),
                    title=slide.title,
                    content=slide.content,
                    image_suggestion=slide.image_suggestion,
                    citations=slide.citations
                )
                for slide in slides_db
            ]
            
            # Handle aspect ratio conversion safely
            aspect_ratio = safe_enum_conversion(AspectRatio, presentation_db.aspect_ratio)
            
            theme = safe_enum_conversion(Theme, presentation_db.theme)
            presentation = Presentation(
                id=presentation_db.id,
                topic=presentation_db.topic,
                num_slides=presentation_db.num_slides,
                slides=slides,
                custom_content=presentation_db.custom_content,
                theme=theme,
                font=presentation_db.font,
                colors=presentation_db.colors,
                aspect_ratio=aspect_ratio,
                custom_width=presentation_db.custom_width,
                custom_height=presentation_db.custom_height,
                created_at=presentation_db.created_at.isoformat() if presentation_db.created_at else None,
                updated_at=presentation_db.updated_at.isoformat() if presentation_db.updated_at else None
            )
            
            # Cache the result
            self.cache.set_presentation(presentation_id, presentation.model_dump())
            
            return presentation
            
        except Exception as e:
            print(f"Error retrieving presentation from database: {e}")
            return None
    
    async def delete_presentation(self, session: AsyncSession, presentation_id: str) -> bool:
        """Delete a presentation from database"""
        try:
            # Delete from cache
            self.cache.delete_presentation(presentation_id)
            
            # Delete slides first (due to foreign key constraint)
            await session.execute(
                delete(SlideDB).where(SlideDB.presentation_id == presentation_id)
            )
            
            # Delete presentation
            await session.execute(
                delete(PresentationDB).where(PresentationDB.id == presentation_id)
            )
            
            await session.commit()
            return True
            
        except Exception as e:
            await session.rollback()
            print(f"Error deleting presentation from database: {e}")
            return False
    
    async def list_presentations(self, session: AsyncSession, limit: int = 100, offset: int = 0) -> List[Presentation]:
        """List presentations from database"""
        try:
            statement = select(PresentationDB).limit(limit).offset(offset)
            result = await session.execute(statement)
            presentations_db = result.scalars().all()
            
            presentations = []
            for presentation_db in presentations_db:
                # Get slides for each presentation
                slides_statement = select(SlideDB).where(
                    SlideDB.presentation_id == presentation_db.id
                ).order_by(SlideDB.slide_order.asc())
                
                slides_result = await session.execute(slides_statement)
                slides_db = slides_result.scalars().all()
                
                slides = [
                    Slide(
                        slide_type=SlideType(slide.slide_type) if not isinstance(slide.slide_type, SlideType) else slide.slide_type,
                        title=slide.title,
                        content=slide.content,
                        image_suggestion=slide.image_suggestion,
                        citations=slide.citations
                    )
                    for slide in slides_db
                ]
                
                # Handle aspect ratio conversion safely
                try:
                    if presentation_db.aspect_ratio:
                        aspect_ratio = AspectRatio(presentation_db.aspect_ratio)
                    else:
                        aspect_ratio = AspectRatio.WIDESCREEN_16_9
                except ValueError:
                    print(f"Warning: Invalid aspect ratio '{presentation_db.aspect_ratio}', defaulting to WIDESCREEN_16_9")
                    aspect_ratio = AspectRatio.WIDESCREEN_16_9
                
                theme = Theme(presentation_db.theme) if not isinstance(presentation_db.theme, Theme) else presentation_db.theme
                presentation = Presentation(
                    id=presentation_db.id,
                    topic=presentation_db.topic,
                    num_slides=presentation_db.num_slides,
                    slides=slides,
                    custom_content=presentation_db.custom_content,
                    theme=theme,
                    font=presentation_db.font,
                    colors=presentation_db.colors,
                    aspect_ratio=aspect_ratio,
                    custom_width=presentation_db.custom_width,
                    custom_height=presentation_db.custom_height,
                    created_at=presentation_db.created_at.isoformat() if presentation_db.created_at else None,
                    updated_at=presentation_db.updated_at.isoformat() if presentation_db.updated_at else None
                )
                
                presentations.append(presentation)
            
            return presentations
            
        except Exception as e:
            print(f"Error listing presentations from database: {e}")
            return []
    
    async def search_presentations(self, session: AsyncSession, topic: str) -> List[Presentation]:
        """Search presentations by topic"""
        try:
            # Use text() for SQL LIKE query
            statement = text("SELECT * FROM presentations WHERE topic LIKE :topic")
            result = await session.execute(statement, {"topic": f"%{topic}%"})
            presentations_db = result.fetchall()
            
            presentations = []
            for presentation_db in presentations_db:
                # Get slides for each presentation
                slides_statement = select(SlideDB).where(
                    SlideDB.presentation_id == presentation_db.id
                ).order_by(SlideDB.slide_order.asc())
                
                slides_result = await session.execute(slides_statement)
                slides_db = slides_result.scalars().all()
                
                slides = [
                    Slide(
                        slide_type=SlideType(slide.slide_type) if not isinstance(slide.slide_type, SlideType) else slide.slide_type,
                        title=slide.title,
                        content=slide.content,
                        image_suggestion=slide.image_suggestion,
                        citations=slide.citations
                    )
                    for slide in slides_db
                ]
                
                # Handle aspect ratio conversion safely
                try:
                    if presentation_db.aspect_ratio:
                        aspect_ratio = AspectRatio(presentation_db.aspect_ratio)
                    else:
                        aspect_ratio = AspectRatio.WIDESCREEN_16_9
                except ValueError:
                    print(f"Warning: Invalid aspect ratio '{presentation_db.aspect_ratio}', defaulting to WIDESCREEN_16_9")
                    aspect_ratio = AspectRatio.WIDESCREEN_16_9
                
                theme = Theme(presentation_db.theme) if not isinstance(presentation_db.theme, Theme) else presentation_db.theme
                presentation = Presentation(
                    id=presentation_db.id,
                    topic=presentation_db.topic,
                    num_slides=presentation_db.num_slides,
                    slides=slides,
                    custom_content=presentation_db.custom_content,
                    theme=theme,
                    font=presentation_db.font,
                    colors=presentation_db.colors,
                    aspect_ratio=aspect_ratio,
                    custom_width=presentation_db.custom_width,
                    custom_height=presentation_db.custom_height,
                    created_at=presentation_db.created_at.isoformat() if presentation_db.created_at else None,
                    updated_at=presentation_db.updated_at.isoformat() if presentation_db.updated_at else None
                )
                
                presentations.append(presentation)
            
            return presentations
            
        except Exception as e:
            print(f"Error searching presentations in database: {e}")
            return [] 