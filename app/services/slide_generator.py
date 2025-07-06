"""
Slide Generator Service
Handles content generation and PPTX file creation
"""
import os
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from pptx import Presentation as PPTXPresentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

from app.models.presentation import Presentation, Slide, SlideType, Theme

class SlideGenerator:
    """Service for generating slides and creating PPTX files"""
    
    def __init__(self):
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_slides(
        self, 
        topic: str, 
        num_slides: int, 
        custom_content: Optional[str] = None,
        theme: Theme = Theme.MODERN,
        font: str = "Arial",
        colors: Optional[Dict[str, str]] = None
    ) -> List[Slide]:
        """
        Generate slides for a given topic
        """
        slides = []
        
        # Generate title slide
        title_slide = Slide(
            slide_type=SlideType.TITLE,
            title=f"{topic}",
            content=[f"Generated on {datetime.now().strftime('%B %d, %Y')}"],
            citations=[]
        )
        slides.append(title_slide)
        
        # Generate content slides
        remaining_slides = num_slides - 1
        if remaining_slides > 0:
            content_slides = await self._generate_content_slides(
                topic, remaining_slides, custom_content
            )
            slides.extend(content_slides)
        
        return slides
    
    async def _generate_content_slides(
        self, 
        topic: str, 
        num_slides: int, 
        custom_content: Optional[str] = None
    ) -> List[Slide]:
        """
        Generate content slides using LLM (placeholder implementation)
        """
        slides = []
        
        # For now, we'll create placeholder content
        # In a real implementation, this would call an LLM API
        
        slide_types = [SlideType.BULLET_POINTS, SlideType.TWO_COLUMN, SlideType.CONTENT_WITH_IMAGE]
        
        for i in range(num_slides):
            slide_type = slide_types[i % len(slide_types)]
            
            if slide_type == SlideType.BULLET_POINTS:
                slide = Slide(
                    slide_type=slide_type,
                    title=f"Key Point {i+1}",
                    content=[
                        f"Important aspect {i+1} of {topic}",
                        f"Supporting detail for point {i+1}",
                        f"Additional information about {topic}",
                        f"Conclusion for section {i+1}"
                    ],
                    citations=[f"Source {i+1}"]
                )
            elif slide_type == SlideType.TWO_COLUMN:
                slide = Slide(
                    slide_type=slide_type,
                    title=f"Comparison {i+1}",
                    content=[
                        f"Column 1: Feature {i+1}",
                        f"Column 2: Benefit {i+1}",
                        f"Column 1: Advantage {i+1}",
                        f"Column 2: Result {i+1}"
                    ],
                    citations=[f"Reference {i+1}"]
                )
            else:  # CONTENT_WITH_IMAGE
                slide = Slide(
                    slide_type=slide_type,
                    title=f"Visual {i+1}",
                    content=[
                        f"Main content about {topic}",
                        f"Supporting text for visual {i+1}",
                        f"Additional context and details"
                    ],
                    image_suggestion=f"Image related to {topic} - section {i+1}",
                    citations=[f"Visual source {i+1}"]
                )
            
            slides.append(slide)
        
        return slides
    
    async def create_pptx(self, presentation: Presentation) -> str:
        """
        Create a PPTX file from a presentation
        """
        # Create a new presentation
        pptx = PPTXPresentation()
        
        # Apply theme and styling
        self._apply_theme(pptx, presentation.theme)
        
        # Create slides
        for slide_data in presentation.slides:
            if slide_data.slide_type == SlideType.TITLE:
                self._create_title_slide(pptx, slide_data, presentation)
            elif slide_data.slide_type == SlideType.BULLET_POINTS:
                self._create_bullet_slide(pptx, slide_data, presentation)
            elif slide_data.slide_type == SlideType.TWO_COLUMN:
                self._create_two_column_slide(pptx, slide_data, presentation)
            elif slide_data.slide_type == SlideType.CONTENT_WITH_IMAGE:
                self._create_content_with_image_slide(pptx, slide_data, presentation)
        
        # Save the presentation
        filename = f"presentation_{presentation.id}.pptx"
        filepath = os.path.join(self.output_dir, filename)
        pptx.save(filepath)
        
        return filepath
    
    def _apply_theme(self, pptx: PPTXPresentation, theme: Theme):
        """Apply theme to presentation"""
        # This is a simplified theme application
        # In a real implementation, you'd apply different slide layouts and styles
        pass
    
    def _create_title_slide(self, pptx: PPTXPresentation, slide_data: Slide, presentation: Presentation):
        """Create a title slide"""
        slide_layout = pptx.slide_layouts[0]  # Title slide layout
        slide = pptx.slides.add_slide(slide_layout)
        
        title = slide.shapes.title
        subtitle = slide.placeholders[1]
        
        title.text = slide_data.title
        subtitle.text = slide_data.content[0] if slide_data.content else ""
    
    def _create_bullet_slide(self, pptx: PPTXPresentation, slide_data: Slide, presentation: Presentation):
        """Create a bullet points slide"""
        slide_layout = pptx.slide_layouts[1]  # Title and content layout
        slide = pptx.slides.add_slide(slide_layout)
        
        title = slide.shapes.title
        content = slide.placeholders[1]
        
        title.text = slide_data.title
        
        text_frame = content.text_frame
        text_frame.clear()
        
        for i, point in enumerate(slide_data.content):
            if i == 0:
                p = text_frame.paragraphs[0]
            else:
                p = text_frame.add_paragraph()
            p.text = point
            p.level = 0
    
    def _create_two_column_slide(self, pptx: PPTXPresentation, slide_data: Slide, presentation: Presentation):
        """Create a two-column slide"""
        slide_layout = pptx.slide_layouts[1]  # Title and content layout
        slide = pptx.slides.add_slide(slide_layout)
        
        title = slide.shapes.title
        title.text = slide_data.title
        
        # Create two text boxes for columns
        left_box = slide.shapes.add_textbox(Inches(0.5), Inches(2), Inches(4), Inches(5))
        right_box = slide.shapes.add_textbox(Inches(5), Inches(2), Inches(4), Inches(5))
        
        # Add content to left column
        left_frame = left_box.text_frame
        left_frame.clear()
        for i, content in enumerate(slide_data.content[::2]):  # Even indices
            if i == 0:
                p = left_frame.paragraphs[0]
            else:
                p = left_frame.add_paragraph()
            p.text = content
        
        # Add content to right column
        right_frame = right_box.text_frame
        right_frame.clear()
        for i, content in enumerate(slide_data.content[1::2]):  # Odd indices
            if i == 0:
                p = right_frame.paragraphs[0]
            else:
                p = right_frame.add_paragraph()
            p.text = content
    
    def _create_content_with_image_slide(self, pptx: PPTXPresentation, slide_data: Slide, presentation: Presentation):
        """Create a content slide with image placeholder"""
        slide_layout = pptx.slide_layouts[1]  # Title and content layout
        slide = pptx.slides.add_slide(slide_layout)
        
        title = slide.shapes.title
        title.text = slide_data.title
        
        # Add content
        content = slide.placeholders[1]
        text_frame = content.text_frame
        text_frame.clear()
        
        for i, point in enumerate(slide_data.content):
            if i == 0:
                p = text_frame.paragraphs[0]
            else:
                p = text_frame.add_paragraph()
            p.text = point
        
        # Add image placeholder
        if slide_data.image_suggestion:
            # Create a placeholder for the image
            img_placeholder = slide.shapes.add_textbox(Inches(6), Inches(2), Inches(3), Inches(4))
            img_frame = img_placeholder.text_frame
            img_frame.clear()
            p = img_frame.paragraphs[0]
            p.text = f"[Image: {slide_data.image_suggestion}]"
            p.alignment = PP_ALIGN.CENTER 