"""
Example OpenAI LLM implementation
This shows how easy it is to swap LLM providers
"""
import asyncio
import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import openai
from app.interfaces.llm import LLMInterface
from app.models.presentation import Slide, SlideType
from app.services.dummy_llm import DummyLLM
from .constants import (
    SAMPLE_OUTPUT_STRUCTURE,
    DEFAULT_MODEL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    FORMAT_TEMPERATURE,
    TITLE_MAX_TOKENS
)

class OpenAILLM(LLMInterface):
    """OpenAI-based LLM implementation"""
    
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model
        self.dummy_llm = DummyLLM()  # Fallback implementation
        self.prompts_dir = os.path.join(os.path.dirname(__file__), 'prompts')
    
    def _load_prompt(self, prompt_file: str) -> str:
        """Load a prompt from a text file"""
        prompt_path = os.path.join(self.prompts_dir, prompt_file)
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    
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
        
        # Load and format the prompt
        prompt_template = self._load_prompt('generate_initial_content.txt')
        additional_context = f'Additional context to incorporate: {custom_content}' if custom_content else ''
        
        prompt = prompt_template.format(
            num_slides=num_slides,
            topic=topic,
            additional_context=additional_context,
            slide_types=', '.join(type_names)
        )
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=DEFAULT_MAX_TOKENS,
            temperature=DEFAULT_TEMPERATURE
        )
        content = response.choices[0].message.content
        return content.strip() if content else ""
    
    async def _format_to_structured_json(self, topic: str, initial_content: str) -> str:
        """Second OpenAI call: Format content into structured JSON"""
        # Load and format the prompt
        prompt_template = self._load_prompt('format_to_structured_json.txt')
        prompt = prompt_template.format(
            topic=topic,
            initial_content=initial_content,
            sample_output=json.dumps(SAMPLE_OUTPUT_STRUCTURE, indent=2)
        )
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=DEFAULT_MAX_TOKENS,
            temperature=FORMAT_TEMPERATURE
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
    
    async def generate_title_slide_content(self, topic: str, custom_content: Optional[str] = None) -> tuple[str, str]:
        """Generate title and subtitle for the title slide using OpenAI"""
        # Load and format the prompt
        prompt_template = self._load_prompt('generate_title_slide_content.txt')
        additional_context = f'Additional context to incorporate: {custom_content}' if custom_content else ''
        
        prompt = prompt_template.format(
            topic=topic,
            additional_context=additional_context
        )
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=TITLE_MAX_TOKENS,
            temperature=DEFAULT_TEMPERATURE
        )
        
        content = response.choices[0].message.content
        if not isinstance(content, str):
            return topic, f"Generated on {datetime.now().strftime('%B %d, %Y')}"
        
        # Parse the response
        parts = content.split('SUBTITLE:')
        title_part = parts[0].replace('TITLE:', '').strip()
        subtitle_part = parts[1].strip() if len(parts) > 1 else f"Generated on {datetime.now().strftime('%B %d, %Y')}"
        
        return title_part, subtitle_part 