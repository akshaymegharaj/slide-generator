# OpenAI LLM Implementation

This directory contains the OpenAI LLM implementation with external prompt files for easy management and editing.

## Structure

```
openai_llm/
├── __init__.py              # Package initialization
├── openai_llm.py           # Main OpenAI LLM implementation
├── constants.py            # Constants and configuration
├── prompts/                # Directory containing all prompt templates
│   ├── generate_initial_content.txt
│   ├── format_to_structured_json.txt
│   └── generate_title_slide_content.txt
└── README.md              # This file
```

## Prompt Files

### generate_initial_content.txt
Generates the initial content for all slides in a presentation. This prompt creates natural language descriptions of each slide including titles, content, and citations.

**Template Variables:**
- `{num_slides}` - Number of slides to generate
- `{topic}` - The presentation topic
- `{additional_context}` - Any custom content to incorporate
- `{slide_types}` - Available slide types (comma-separated)

### format_to_structured_json.txt
Formats the initial content into structured JSON format that can be parsed into Slide objects.

**Template Variables:**
- `{topic}` - The presentation topic
- `{initial_content}` - The content from the first step
- `{sample_output}` - Example JSON structure

### generate_title_slide_content.txt
Generates the title and subtitle for the title slide.

**Template Variables:**
- `{topic}` - The presentation topic
- `{additional_context}` - Any custom content to incorporate

## Constants File

The `constants.py` file contains:

- **SAMPLE_OUTPUT_STRUCTURE**: JSON structure used in the formatting prompt
- **DEFAULT_SLIDE_TYPES**: Default slide types when none are specified
- **OpenAI API Configuration**: Model, max tokens, temperature settings

This keeps the main code clean and makes configuration easy to modify.

## Modifying Prompts

To modify any prompt:

1. Edit the corresponding `.txt` file in the `prompts/` directory
2. Use the template variables listed above with `{variable_name}` syntax
3. The changes will take effect immediately without needing to restart the application

## Benefits

- **Easy Editing**: Prompts can be modified without touching Python code
- **Version Control**: Prompt changes can be tracked separately from code changes
- **Collaboration**: Non-developers can easily edit prompts
- **Testing**: Different prompt versions can be tested by simply swapping files
- **Maintenance**: Prompts are clearly separated and organized
- **Clean Code**: Constants and configuration are separated from business logic
- **Readability**: Large data structures don't break the reading flow of the code

## Usage

```python
from app.services.impl.openai_llm import OpenAILLM

# Create instance
llm = OpenAILLM(api_key="your-api-key")

# Generate slides
slides = await llm.generate_slides_content("AI in Healthcare", 5)

# Generate title slide
title, subtitle = await llm.generate_title_slide_content("AI in Healthcare")
``` 