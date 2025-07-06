"""
Example OpenAI LLM implementation
This shows how easy it is to swap LLM providers
"""
import asyncio
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
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
        You are an expert presentation designer and content creator. Create {num_slides} engaging, informative slides about "{topic}".
        
        {f'Additional context to incorporate: {custom_content}' if custom_content else ''}
        
        Available slide types: {', '.join(type_names)}
        
        For each slide, provide:
        1. Slide type (choose from available types)
        2. Slide title (3-8 words, engaging and descriptive)
        3. Content appropriate for that slide type:
           - For bullet_points: 4-5 compelling bullet points with actionable insights
           - For two_column: 4-6 alternating column items that create meaningful comparisons
           - For content_with_image: 3-4 content points + specific image suggestion that enhances understanding
        4. Citations (2-3 relevant sources):
           - Academic papers, industry reports, expert sources, or authoritative references
           - Should be relevant to the specific content of that slide
           - Include author names, publication years, or source names where appropriate
        
        Guidelines:
        - Make content informative, engaging, and professional
        - Include specific examples, data points, or actionable insights where relevant
        - Ensure logical flow and progression between slides
        - Use clear, concise language that's easy to understand
        - Make each slide valuable and memorable for the audience
        - Provide realistic, relevant citations for each slide's content
        
        Format your response as a natural text description of each slide, including the citations for each slide.
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
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
        
        IMPORTANT: Extract and include the citations mentioned in the original content for each slide. If no citations are provided in the original content, generate 2-3 realistic, relevant citations for each slide based on the content.
        
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
        Generate a compelling and engaging title for slide {slide_number} about "{topic}".
        Slide type: {slide_type.value}
        
        Guidelines:
        - Title should be 3-8 words
        - Capture the main point and value proposition of the slide
        - Be memorable and attention-grabbing
        - Use active, engaging language
        - Avoid generic or boring titles
        
        The title should make the audience want to learn more about what's on the slide.
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
            temperature=0.7
        )
        content = response.choices[0].message.content
        return content.strip().strip('"') if content else ""
    
    async def generate_title_slide_content(self, topic: str, custom_content: Optional[str] = None) -> tuple[str, str]:
        """Generate title and subtitle for the title slide using OpenAI"""
        prompt = f"""
        Create an engaging title slide for a presentation about "{topic}".
        {f'Additional context to incorporate: {custom_content}' if custom_content else ''}
        
        Provide:
        1. A compelling main title (3-8 words) that captures the essence of the topic
        2. An engaging subtitle (1-2 lines) that provides context or adds value
        
        Guidelines:
        - Main title should be memorable and attention-grabbing
        - Subtitle should provide context, value proposition, or key insight
        - Use active, engaging language
        - Make it professional yet compelling
        - Avoid generic or boring titles
        
        Format the response as:
        TITLE:
        [main title]
        
        SUBTITLE:
        [subtitle]
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not isinstance(content, str):
            return topic, f"Generated on {datetime.now().strftime('%B %d, %Y')}"
        
        # Parse the response
        parts = content.split('SUBTITLE:')
        title_part = parts[0].replace('TITLE:', '').strip()
        subtitle_part = parts[1].strip() if len(parts) > 1 else f"Generated on {datetime.now().strftime('%B %d, %Y')}"
        
        return title_part, subtitle_part
    
    async def generate_bullet_points(self, topic: str, slide_title: str, custom_content: Optional[str] = None) -> List[str]:
        """Generate bullet points for a slide using OpenAI"""
        prompt = f"""
        Generate 4-5 compelling bullet points for a slide titled "{slide_title}" about "{topic}".
        {f'Additional context to incorporate: {custom_content}' if custom_content else ''}
        
        Each bullet point should be:
        - Concise but impactful (1-2 lines)
        - Informative with specific insights or actionable information
        - Professional yet engaging in tone
        - Include concrete examples, data points, or practical takeaways where relevant
        - Build upon each other to create a coherent narrative
        
        Guidelines:
        - Start with the most important point
        - Use active voice and strong verbs
        - Include specific details rather than generic statements
        - Make each point memorable and valuable to the audience
        
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
        Generate compelling content for a two-column slide titled "{slide_title}" about "{topic}".
        {f'Additional context to incorporate: {custom_content}' if custom_content else ''}
        
        Create 4-6 alternating items for the two columns that create meaningful comparisons:
        - Column 1: Features, facts, concepts, challenges, or current state
        - Column 2: Benefits, explanations, solutions, or future state
        
        Guidelines:
        - Make comparisons meaningful and insightful
        - Use specific examples and concrete details
        - Ensure logical pairing between columns
        - Include actionable insights or practical takeaways
        - Make the comparison valuable for the audience
        
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
        Generate compelling content for a slide titled "{slide_title}" about "{topic}" that will include an image.
        {f'Additional context to incorporate: {custom_content}' if custom_content else ''}
        
        Provide:
        1. 3-4 content points (1-2 lines each) that are informative and engaging
        2. A specific image suggestion that would enhance understanding and complement the content
        
        Guidelines for content:
        - Make each point valuable and memorable
        - Include specific examples or insights where relevant
        - Use clear, concise language
        - Ensure points work together to tell a coherent story
        
        Guidelines for image:
        - Suggest specific, relevant images (e.g., "Infographic showing data flow", "Diagram of system architecture")
        - Images should enhance understanding, not just decorate
        - Be specific about what the image should show
        
        Format the response as:
        CONTENT:
        [content points, one per line]
        
        IMAGE:
        [specific image suggestion]
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
        Generate 2-3 realistic, relevant citations for the following content about "{topic}".
        
        Content to cite:
        {content_str}
        
        The citations should be:
        - Academic papers, industry reports, expert sources, or authoritative references
        - Specifically relevant to the content provided
        - Include author names, publication years, or source names where appropriate
        - Realistic and credible for the topic
        - Properly formatted as complete citations
        
        Guidelines:
        - Make citations specific to the actual content points
        - Include recent sources (within last 5-10 years) when appropriate
        - Use credible sources that would actually exist for this topic
        - Format as complete citations (e.g., "Smith, J. (2023). Title of Paper. Journal Name.")
        
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