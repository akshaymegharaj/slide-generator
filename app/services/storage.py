"""
Storage Service for managing presentation data
"""
import os
import json
from typing import Optional, Dict, Any
from datetime import datetime

from app.models.presentation import Presentation

class PresentationStorage:
    """Service for storing and retrieving presentations"""
    
    def __init__(self):
        self.storage_dir = "storage"
        os.makedirs(self.storage_dir, exist_ok=True)
    
    async def save_presentation(self, presentation: Presentation) -> bool:
        """
        Save a presentation to storage
        """
        try:
            # Add timestamps
            if not presentation.created_at:
                presentation.created_at = datetime.now().isoformat()
            presentation.updated_at = datetime.now().isoformat()
            
            # Convert to dict for JSON serialization
            presentation_dict = presentation.model_dump()
            
            # Save to file
            filename = f"{presentation.id}.json"
            filepath = os.path.join(self.storage_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(presentation_dict, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving presentation: {e}")
            return False
    
    async def get_presentation(self, presentation_id: str) -> Optional[Presentation]:
        """
        Retrieve a presentation from storage
        """
        try:
            filename = f"{presentation_id}.json"
            filepath = os.path.join(self.storage_dir, filename)
            
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r') as f:
                presentation_dict = json.load(f)
            
            # Convert back to Presentation object
            presentation = Presentation(**presentation_dict)
            return presentation
            
        except Exception as e:
            print(f"Error retrieving presentation: {e}")
            return None
    
    async def delete_presentation(self, presentation_id: str) -> bool:
        """
        Delete a presentation from storage
        """
        try:
            filename = f"{presentation_id}.json"
            filepath = os.path.join(self.storage_dir, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
            
        except Exception as e:
            print(f"Error deleting presentation: {e}")
            return False
    
    async def list_presentations(self) -> list:
        """
        List all stored presentations
        """
        try:
            presentations = []
            
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json'):
                    presentation_id = filename.replace('.json', '')
                    presentation = await self.get_presentation(presentation_id)
                    if presentation:
                        presentations.append(presentation)
            
            return presentations
            
        except Exception as e:
            print(f"Error listing presentations: {e}")
            return [] 