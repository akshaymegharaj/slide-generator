"""
Example OpenAI LLM implementation
This shows how easy it is to swap LLM providers
"""
import asyncio
import json
from typing import List, Optional, Dict, Any
import openai
from app.interfaces.llm import LLMInterface
from app.models.presentation import Slide, SlideType
from app.services.dummy_llm import DummyLLM

class OpenAILLM(LLMInterface):
    """OpenAI-based LLM implementation"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model
        self.dummy_llm = DummyLLM()  # Fallback implementation
    
    async def generate_slides_content(
        self, 
        topic: str, 
        num_slides: int, 
        custom_content: Optional[str] = None,
        slide_types: Optional[List[SlideType]] = None
    ) -> List[Slide]:
        """Generate slide content using OpenAI with two-step approach"""
        try:
            # Gpt performs well when asked to do one task at a time, so content generation & formatting are separated into two separate calls
            
            # Step 1: Generate initial content and slide types
            initial_content = await self._generate_initial_content(topic, num_slides, custom_content, slide_types)
            
            # Step 2: Format content into structured JSON
            structured_content = await self._format_to_structured_json(topic, initial_content)
            
            # Parse the structured content and create Slide objects
            slides = self._parse_structured_content(structured_content)
            
            return slides
            
        except Exception as e:
            print(f"OpenAI LLM failed, falling back to dummy LLM: {str(e)}")
            # Fallback to dummy LLM in case of parsing error or API failure
            return await self.dummy_llm.generate_slides_content(topic, num_slides, custom_content, slide_types)
    
    async def _generate_initial_content(
        self, 
        topic: str, 
        num_slides: int, 
        custom_content: Optional[str] = None,
        slide_types: Optional[List[SlideType]] = None
    ) -> str:
        """First OpenAI call: Generate initial content and slide types"""
        available_types = slide_types or [SlideType.BULLET_POINTS, SlideType.TWO_COLUMN, SlideType.CONTENT_WITH_IMAGE]
        type_names = [t.value for t in available_types]
        
        prompt = f"""
        Create {num_slides} slides about "{topic}".
        {f'Custom content to include: {custom_content}' if custom_content else ''}
        
        Available slide types: {', '.join(type_names)}
        
        For each slide, provide:
        1. Slide type (choose from available types)
        2. Slide title (3-8 words)
        3. Content appropriate for that slide type:
           - For bullet_points: 4-5 bullet points
           - For two_column: 4-6 alternating column items
           - For content_with_image: 3-4 content points + image suggestion
        
        Format your response as a natural text description of each slide.
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7
        )
        content = response.choices[0].message.content
        return content.strip() if content else ""
    
    async def _format_to_structured_json(self, topic: str, initial_content: str) -> str:
        """Second OpenAI call: Format content into structured JSON"""
        sample_output = {
            "slides": [
                {
                    "slide_type": "bullet_points",
                    "title": "Introduction to Topic",
                    "content": [
                        "Key point about the topic",
                        "Important aspect to consider",
                        "Supporting detail",
                        "Conclusion or summary"
                    ],
                    "image_suggestion": None,
                    "citations": [
                        "Research paper on topic (2023)",
                        "Industry report on topic"
                    ]
                },
                {
                    "slide_type": "two_column",
                    "title": "Features vs Benefits",
                    "content": [
                        "Column 1: Feature 1",
                        "Column 2: Benefit 1",
                        "Column 1: Feature 2",
                        "Column 2: Benefit 2"
                    ],
                    "image_suggestion": None,
                    "citations": [
                        "Expert analysis on topic"
                    ]
                },
                {
                    "slide_type": "content_with_image",
                    "title": "Visual Overview",
                    "content": [
                        "Main content point",
                        "Supporting information",
                        "Additional context"
                    ],
                    "image_suggestion": "Diagram showing topic relationships",
                    "citations": [
                        "Visual guide on topic"
                    ]
                }
            ]
        }
        
        prompt = f"""
        Based on the following content about "{topic}", format it into a structured JSON response.
        
        Original content:
        {initial_content}
        
        Please format this into the exact JSON structure shown below. Use the slide_type values: "bullet_points", "two_column", "content_with_image".
        
        Sample output structure:
        {json.dumps(sample_output, indent=2)}
        
        Return ONLY the JSON object, no additional text or explanations.
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.3  # Lower temperature for more consistent formatting
        )
        content = response.choices[0].message.content
        return content.strip() if content else ""
    
    def _parse_structured_content(self, json_content: str) -> List[Slide]:
        """Parse the structured JSON content into Slide objects"""
        try:
            # Clean the response to extract just the JSON
            json_str = json_content.strip()
            if json_str.startswith('```json'):
                json_str = json_str[7:]
            if json_str.endswith('```'):
                json_str = json_str[:-3]
            
            data = json.loads(json_str)
            slides = []
            
            for slide_data in data.get('slides', []):
                slide_type = SlideType(slide_data.get('slide_type', 'bullet_points'))
                title = slide_data.get('title', 'Untitled Slide')
                content = slide_data.get('content', [])
                if not isinstance(content, list):
                    content = []
                image_suggestion = slide_data.get('image_suggestion')
                citations = slide_data.get('citations', [])
                
                slide = Slide(
                    slide_type=slide_type,
                    title=title,
                    content=content,
                    image_suggestion=image_suggestion,
                    citations=citations
                )
                slides.append(slide)
            
            return slides
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise Exception(f"Failed to parse structured content: {str(e)}")
    
    async def generate_slide_title(self, topic: str, slide_number: int, slide_type: SlideType) -> str:
        """Generate a title for a specific slide using OpenAI"""
        prompt = f"""
        Generate a concise and engaging title for slide {slide_number} about "{topic}".
        Slide type: {slide_type.value}
        The title should be 3-8 words and capture the main point of the slide.
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
            temperature=0.7
        )
        content = response.choices[0].message.content
        return content.strip().strip('"') if content else ""
    
    async def generate_bullet_points(self, topic: str, slide_title: str, custom_content: Optional[str] = None) -> List[str]:
        """Generate bullet points for a slide using OpenAI"""
        prompt = f"""
        Generate 4-5 bullet points for a slide titled "{slide_title}" about "{topic}".
        {f'Custom content to include: {custom_content}' if custom_content else ''}
        
        Each bullet point should be:
        - Concise (1-2 lines)
        - Informative and relevant
        - Professional in tone
        
        Return only the bullet points, one per line, without numbering or formatting.
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not isinstance(content, str):
            return []
        return [line.strip('- ').strip() for line in content.split('\n') if line.strip()]
    
    async def generate_two_column_content(self, topic: str, slide_title: str, custom_content: Optional[str] = None) -> List[str]:
        """Generate content for a two-column slide using OpenAI"""
        prompt = f"""
        Generate content for a two-column slide titled "{slide_title}" about "{topic}".
        {f'Custom content to include: {custom_content}' if custom_content else ''}
        
        Create 4-6 alternating items for the two columns:
        - Column 1: Features, facts, or concepts
        - Column 2: Benefits, explanations, or results
        
        Format as: "Column 1: [content]" and "Column 2: [content]"
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not isinstance(content, str):
            return []
        return [line.strip() for line in content.split('\n') if line.strip()]
    
    async def generate_content_with_image(self, topic: str, slide_title: str, custom_content: Optional[str] = None) -> tuple[List[str], str]:
        """Generate content and image suggestion for a slide with image using OpenAI"""
        prompt = f"""
        Generate content for a slide titled "{slide_title}" about "{topic}" that will include an image.
        {f'Custom content to include: {custom_content}' if custom_content else ''}
        
        Provide:
        1. 3-4 content points (1-2 lines each)
        2. An image suggestion that would complement the content
        
        Format the response as:
        CONTENT:
        [content points, one per line]
        
        IMAGE:
        [image suggestion]
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not isinstance(content, str):
            return [], ""
        # Parse the response
        parts = content.split('IMAGE:')
        content_part = parts[0].replace('CONTENT:', '').strip()
        image_part = parts[1].strip() if len(parts) > 1 else f"Image related to {topic}"
        content_lines = [line.strip() for line in content_part.split('\n') if line.strip()]
        return content_lines, image_part
    
    async def generate_citations(self, topic: str, content: List[str]) -> List[str]:
        """Generate citations for slide content using OpenAI"""
        if isinstance(content, list):
            content_str = '\n'.join(content)
        elif content is None:
            content_str = ''
        else:
            content_str = str(content)
        prompt = f"""
        Generate 2-3 realistic citations for content about "{topic}".
        The citations should be:
        - Academic papers, industry reports, or expert sources
        - Relevant to the topic
        - Properly formatted
        
        Content:
        {content_str}
        
        Return only the citations, one per line.
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.5
        )
        
        content = response.choices[0].message.content
        if not isinstance(content, str):
            return []
        return [line.strip() for line in content.split('\n') if line.strip()][:3]
    
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