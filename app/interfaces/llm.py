"""
Abstract LLM interface for different language model providers
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.models.presentation import Slide, SlideType

class LLMInterface(ABC):
    """Abstract interface for LLM operations"""
    
    @abstractmethod
    async def generate_slides_content(
        self, 
        topic: str, 
        num_slides: int, 
        custom_content: Optional[str] = None,
        slide_types: Optional[List[SlideType]] = None
    ) -> List[Slide]:
        """Generate slide content using LLM"""
        pass
    
    @abstractmethod
    async def generate_slide_title(self, topic: str, slide_number: int, slide_type: SlideType) -> str:
        """Generate a title for a specific slide"""
        pass
    
    @abstractmethod
    async def generate_bullet_points(self, topic: str, slide_title: str, custom_content: Optional[str] = None) -> List[str]:
        """Generate bullet points for a slide"""
        pass
    
    @abstractmethod
    async def generate_two_column_content(self, topic: str, slide_title: str, custom_content: Optional[str] = None) -> List[str]:
        """Generate content for a two-column slide"""
        pass
    
    @abstractmethod
    async def generate_content_with_image(self, topic: str, slide_title: str, custom_content: Optional[str] = None) -> tuple[List[str], str]:
        """Generate content and image suggestion for a slide with image"""
        pass
    
    @abstractmethod
    async def generate_citations(self, topic: str, content: List[str]) -> List[str]:
        """Generate citations for slide content"""
        pass 