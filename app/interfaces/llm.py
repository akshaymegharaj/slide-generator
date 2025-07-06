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