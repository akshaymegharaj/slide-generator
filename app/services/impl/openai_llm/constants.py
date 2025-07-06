"""
Constants for OpenAI LLM implementation
"""

# Sample output structure for JSON formatting prompt
SAMPLE_OUTPUT_STRUCTURE = {
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

# Default slide types when none are specified
DEFAULT_SLIDE_TYPES = ["bullet_points", "two_column", "content_with_image"]

# OpenAI API configuration
DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_MAX_TOKENS = 1500
DEFAULT_TEMPERATURE = 0.7
FORMAT_TEMPERATURE = 0.3  # Lower temperature for more consistent formatting
TITLE_MAX_TOKENS = 100 