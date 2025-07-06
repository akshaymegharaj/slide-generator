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
    "font": "Calibri",
    "colors": {
      "primary": "#1f4e79",
      "secondary": "#d32f2f",
      "background": "#ffffff",
      "text": "#333333"
    }
  }'
```

## Example Workflow

1. **Check API health:**
   ```bash
   curl -X GET "http://localhost:8000/"
   ```

2. **Create a presentation:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/presentations" \
     -H "Content-Type: application/json" \
     -d '{
       "topic": "Python Web Development",
       "num_slides": 3,
       "custom_content": "Focus on FastAPI and modern web development practices"
     }'
   ```

3. **List presentations to get the ID:**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/presentations"
   ```

4. **Get specific presentation (replace UUID):**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/presentations/ec8b6f43-723c-46c7-809a-43befe3b7ea9"
   ```

5. **Configure the presentation (replace UUID):**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/presentations/ec8b6f43-723c-46c7-809a-43befe3b7ea9/configure" \
     -H "Content-Type: application/json" \
     -d '{
       "theme": "modern",
       "font": "Arial",
       "colors": {
         "primary": "#2196F3",
         "secondary": "#FF5722",
         "background": "#FAFAFA",
         "text": "#212121"
       }
     }'
   ```

6. **Download the presentation (replace UUID):**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/presentations/ec8b6f43-723c-46c7-809a-43befe3b7ea9/download" \
     --output "python_web_dev_presentation.pptx"
   ```

## Available Themes
- `modern`
- `classic`
- `minimal`
- `corporate`

## Notes
- All presentation IDs are UUIDs
- The `num_slides` parameter accepts values between 1-20
- The `topic` field has a maximum length of 200 characters
- The `custom_content` field has a maximum length of 2000 characters
- Colors should be provided in hexadecimal format (e.g., "#FF5722") 