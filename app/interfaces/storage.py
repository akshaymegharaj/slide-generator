"""
Abstract storage interface for different storage backends
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.presentation import Presentation

class StorageInterface(ABC):
    """Abstract interface for storage operations"""
    
    @abstractmethod
    async def save_presentation(self, session: AsyncSession, presentation: Presentation) -> bool:
        """Save a presentation to storage"""
        pass
    
    @abstractmethod
    async def get_presentation(self, session: AsyncSession, presentation_id: str) -> Optional[Presentation]:
        """Retrieve a presentation from storage"""
        pass
    
    @abstractmethod
    async def delete_presentation(self, session: AsyncSession, presentation_id: str) -> bool:
        """Delete a presentation from storage"""
        pass
    
    @abstractmethod
    async def list_presentations(self, session: AsyncSession, limit: int = 100, offset: int = 0) -> List[Presentation]:
        """List presentations from storage"""
        pass
    
    @abstractmethod
    async def search_presentations(self, session: AsyncSession, topic: str) -> List[Presentation]:
        """Search presentations by topic"""
        pass 