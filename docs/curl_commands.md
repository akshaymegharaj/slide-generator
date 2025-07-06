# Slide Generator API - Curl Commands

Base URL: `http://localhost:8000`

## Health Check
```bash
curl -X GET "http://localhost:8000/"
```

## Cache Management

### Get Cache Statistics
```bash
curl -X GET "http://localhost:8000/api/v1/cache/stats"
```

### Clear All Caches
```bash
curl -X POST "http://localhost:8000/api/v1/cache/clear"
```

## LLM Service Management

### Get LLM Service Status
```bash
curl -X GET "http://localhost:8000/api/v1/llm/status"
```

### Switch LLM Service
```bash
# Switch to Dummy LLM (default)
curl -X POST "http://localhost:8000/api/v1/llm/switch" \
  -H "Content-Type: application/json" \
  -d '{"llm_type": "dummy"}'

# Switch to OpenAI LLM (requires API key)
curl -X POST "http://localhost:8000/api/v1/llm/switch" \
  -H "Content-Type: application/json" \
  -d '{
    "llm_type": "openai",
    "api_key": "your-openai-api-key-here"
  }'
```

## Concurrency Management

### Get Concurrency Statistics
```bash
curl -X GET "http://localhost:8000/api/v1/concurrency/stats"
```

## Aspect Ratios

### Get Available Aspect Ratios
```bash
curl -X GET "http://localhost:8000/api/v1/aspect-ratios"
```

## Presentations

### Create a New Presentation
```bash
curl -X POST "http://localhost:8000/api/v1/presentations" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Introduction to Machine Learning",
    "num_slides": 5,
    "custom_content": "Focus on practical applications and real-world examples"
  }'
```

### List All Presentations
```bash
# Get all presentations (default: limit=100, offset=0)
curl -X GET "http://localhost:8000/api/v1/presentations"

# With pagination
curl -X GET "http://localhost:8000/api/v1/presentations?limit=10&offset=0"
```

### Search Presentations by Topic
```bash
curl -X GET "http://localhost:8000/api/v1/presentations/search/Machine"
```

### Get Specific Presentation
```bash
# Replace {presentation_id} with actual UUID
curl -X GET "http://localhost:8000/api/v1/presentations/{presentation_id}"
```

### Delete Presentation
```bash
# Replace {presentation_id} with actual UUID
curl -X DELETE "http://localhost:8000/api/v1/presentations/{presentation_id}"
```

### Download Presentation as PPTX
```bash
# Replace {presentation_id} with actual UUID
curl -X GET "http://localhost:8000/api/v1/presentations/{presentation_id}/download" \
  --output "presentation.pptx"
```

### Configure Presentation
```bash
# Replace {presentation_id} with actual UUID
curl -X POST "http://localhost:8000/api/v1/presentations/{presentation_id}/configure" \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "corporate",
    "font": "Roboto",
    "colors": {
      "primary": "#3498DB",
      "secondary": "#2ECC71",
      "background": "#1A1A2E",
      "text": "#E8E8E8",
      "accent": "#F39C12"
    },
    "aspect_ratio": "16:9",
    "custom_width": null,
    "custom_height": null
  }'
```

## Example Workflow

1. **Check API health:**
   ```bash
   curl -X GET "http://localhost:8000/"
   ```

2. **Check LLM service status:**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/llm/status"
   ```

3. **Get available aspect ratios:**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/aspect-ratios"
   ```

4. **Create a presentation:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/presentations" \
     -H "Content-Type: application/json" \
     -d '{
       "topic": "Python Web Development",
       "num_slides": 3,
       "custom_content": "Focus on FastAPI and modern web development practices"
     }'
   ```

5. **List presentations to get the ID:**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/presentations"
   ```

6. **Get specific presentation (replace UUID):**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/presentations/ec8b6f43-723c-46c7-809a-43befe3b7ea9"
   ```

7. **Configure the presentation (replace UUID):**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/presentations/ec8b6f43-723c-46c7-809a-43befe3b7ea9/configure" \
     -H "Content-Type: application/json" \
     -d '{
       "theme": "modern",
       "font": "Segoe UI",
       "colors": {
         "primary": "#2E86AB",
         "secondary": "#A23B72",
         "background": "#FFFFFF",
         "text": "#2C3E50",
         "accent": "#3498DB"
       },
       "aspect_ratio": "16:9"
     }'
   ```

8. **Download the presentation (replace UUID):**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/presentations/ec8b6f43-723c-46c7-809a-43befe3b7ea9/download" \
     --output "python_web_dev_presentation.pptx"
   ```

## Available Themes
- `modern` - Clean, vibrant design with blue-purple gradient
- `classic` - Traditional business look with navy and gold
- `minimal` - Simple, clean design with black background
- `corporate` - Professional business look with dark blue background

## Available Aspect Ratios
- `16:9` - Widescreen (13.33" x 7.5") - Standard widescreen format
- `4:3` - Standard (10" x 7.5") - Traditional standard format
- `A4` - A4 Portrait (8.27" x 11.69") - A4 paper ratio in portrait
- `A4_L` - A4 Landscape (11.69" x 8.27") - A4 paper ratio in landscape
- `1:1` - Square (10" x 10") - Square format for social media
- `custom` - Custom dimensions (5-20 inches each)

## Request/Response Schema

### PresentationCreate
```json
{
  "topic": "string (1-200 chars)",
  "num_slides": "integer (1-20)",
  "custom_content": "string (optional, max 2000 chars)"
}
```

### PresentationConfig
```json
{
  "theme": "string (optional, enum: modern, classic, minimal, corporate)",
  "font": "string (optional)",
  "colors": {
    "primary": "string (hex color)",
    "secondary": "string (hex color)",
    "background": "string (hex color)",
    "text": "string (hex color)",
    "accent": "string (hex color)"
  },
  "aspect_ratio": "string (optional, enum: 16:9, 4:3, A4, A4_L, 1:1, custom)",
  "custom_width": "float (optional, 5.0-20.0 inches)",
  "custom_height": "float (optional, 5.0-20.0 inches)"
}
```

### Presentation (Response)
```json
{
  "id": "string (UUID)",
  "topic": "string",
  "num_slides": "integer",
  "slides": [
    {
      "slide_type": "string (enum: title, bullet_points, two_column, content_with_image)",
      "title": "string",
      "content": ["string"],
      "image_suggestion": "string (optional)",
      "citations": ["string"]
    }
  ],
  "custom_content": "string (optional)",
  "theme": "string",
  "font": "string",
  "colors": {
    "primary": "string",
    "secondary": "string",
    "background": "string",
    "text": "string",
    "accent": "string"
  },
  "aspect_ratio": "string",
  "custom_width": "float (optional)",
  "custom_height": "float (optional)",
  "created_at": "string (ISO format)",
  "updated_at": "string (ISO format)"
}
```

## Notes
- All presentation IDs are UUIDs
- The `num_slides` parameter accepts values between 1-20
- The `topic` field has a maximum length of 200 characters
- The `custom_content` field has a maximum length of 2000 characters
- Colors should be provided in hexadecimal format (e.g., "#FF5722")
- Custom dimensions must be between 5.0 and 20.0 inches
- The API includes rate limiting, authentication, and concurrency control middleware
- Cache statistics and management are available for performance monitoring 