"""
Dummy LLM implementation for testing and development
"""
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.interfaces.llm import LLMInterface
from app.models.presentation import Slide, SlideType

class DummyLLM(LLMInterface):
    """Dummy LLM implementation that generates placeholder content"""
    
    def __init__(self):
        self.delay_simulation = 0.1  # Simulate API delay
    
    async def generate_slides_content(
        self, 
        topic: str, 
        num_slides: int, 
        custom_content: Optional[str] = None,
        slide_types: Optional[List[SlideType]] = None
    ) -> List[Slide]:
        """Generate slide content using dummy LLM"""
        await asyncio.sleep(self.delay_simulation)  # Simulate API call
        
        slides = []
        available_types = slide_types or [SlideType.BULLET_POINTS, SlideType.TWO_COLUMN, SlideType.CONTENT_WITH_IMAGE]
        
        for i in range(num_slides):
            slide_type = available_types[i % len(available_types)]
            
            if slide_type == SlideType.BULLET_POINTS:
                slide = await self._create_bullet_points_slide(topic, i + 1, custom_content)
            elif slide_type == SlideType.TWO_COLUMN:
                slide = await self._create_two_column_slide(topic, i + 1, custom_content)
            elif slide_type == SlideType.CONTENT_WITH_IMAGE:
                slide = await self._create_content_with_image_slide(topic, i + 1, custom_content)
            else:
                slide = await self._create_bullet_points_slide(topic, i + 1, custom_content)
            
            slides.append(slide)
        
        return slides
    
    async def generate_title_slide_content(self, topic: str, custom_content: Optional[str] = None) -> tuple[str, str]:
        """Generate title and subtitle for the title slide"""
        await asyncio.sleep(self.delay_simulation)
        
        title = f"{topic}"
        subtitle = f"Generated on {datetime.now().strftime('%B %d, %Y')}"
        
        if custom_content:
            subtitle = f"{custom_content[:50]}... | {subtitle}"
        
        return title, subtitle
    
    async def generate_slide_title(self, topic: str, slide_number: int, slide_type: SlideType) -> str:
        """Generate a title for a specific slide"""
        await asyncio.sleep(self.delay_simulation)
        
        titles = {
            SlideType.BULLET_POINTS: f"Key Point {slide_number}",
            SlideType.TWO_COLUMN: f"Comparison {slide_number}",
            SlideType.CONTENT_WITH_IMAGE: f"Visual {slide_number}",
            SlideType.TITLE: f"{topic}"
        }
        
        return titles.get(slide_type, f"Slide {slide_number}")
    
    async def generate_bullet_points(self, topic: str, slide_title: str, custom_content: Optional[str] = None) -> List[str]:
        """Generate bullet points for a slide"""
        await asyncio.sleep(self.delay_simulation)
        
        base_points = [
            f"Important aspect of {topic}",
            f"Supporting detail for {slide_title}",
            f"Additional information about {topic}",
            f"Conclusion for {slide_title}"
        ]
        
        if custom_content:
            base_points.append(f"Custom content: {custom_content[:50]}...")
        
        return base_points
    
    async def generate_two_column_content(self, topic: str, slide_title: str, custom_content: Optional[str] = None) -> List[str]:
        """Generate content for a two-column slide"""
        await asyncio.sleep(self.delay_simulation)
        
        content = [
            f"Column 1: Feature of {topic}",
            f"Column 2: Benefit of {topic}",
            f"Column 1: Advantage of {topic}",
            f"Column 2: Result of {topic}"
        ]
        
        if custom_content:
            content.extend([
                f"Column 1: Custom aspect",
                f"Column 2: Custom benefit"
            ])
        
        return content
    
    async def generate_content_with_image(self, topic: str, slide_title: str, custom_content: Optional[str] = None) -> tuple[List[str], str]:
        """Generate content and image suggestion for a slide with image"""
        await asyncio.sleep(self.delay_simulation)
        
        content = [
            f"Main content about {topic}",
            f"Supporting text for {slide_title}",
            f"Additional context and details"
        ]
        
        if custom_content:
            content.append(f"Custom content: {custom_content[:50]}...")
        
        image_suggestion = f"Image related to {topic} - {slide_title}"
        
        return content, image_suggestion
    
    async def generate_citations(self, topic: str, content: List[str]) -> List[str]:
        """Generate citations for slide content"""
        await asyncio.sleep(self.delay_simulation)
        
        citations = [
            f"Research paper on {topic}",
            f"Industry report on {topic}",
            f"Expert analysis of {topic}"
        ]
        
        return citations[:2]  # Limit to 2 citations
    
    async def _create_bullet_points_slide(self, topic: str, slide_number: int, custom_content: Optional[str] = None) -> Slide:
        """Create a bullet points slide"""
        title = await self.generate_slide_title(topic, slide_number, SlideType.BULLET_POINTS)
        content = await self.generate_bullet_points(topic, title, custom_content)
        citations = await self.generate_citations(topic, content)
        
        return Slide(
            slide_type=SlideType.BULLET_POINTS,
            title=title,
            content=content,
            citations=citations
        )
    
    async def _create_two_column_slide(self, topic: str, slide_number: int, custom_content: Optional[str] = None) -> Slide:
        """Create a two-column slide"""
        title = await self.generate_slide_title(topic, slide_number, SlideType.TWO_COLUMN)
        content = await self.generate_two_column_content(topic, title, custom_content)
        citations = await self.generate_citations(topic, content)
        
        return Slide(
            slide_type=SlideType.TWO_COLUMN,
            title=title,
            content=content,
            citations=citations
        )
    
    async def _create_content_with_image_slide(self, topic: str, slide_number: int, custom_content: Optional[str] = None) -> Slide:
        """Create a content with image slide"""
        title = await self.generate_slide_title(topic, slide_number, SlideType.CONTENT_WITH_IMAGE)
        content, image_suggestion = await self.generate_content_with_image(topic, title, custom_content)
        citations = await self.generate_citations(topic, content)
        
        return Slide(
            slide_type=SlideType.CONTENT_WITH_IMAGE,
            title=title,
            content=content,
            image_suggestion=image_suggestion,
            citations=citations
        ) 