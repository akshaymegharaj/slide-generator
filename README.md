# Slide Generator API

A modern API for generating customizable presentation slides using AI. Built with FastAPI, SQLite, and modular architecture.

## Features

- 🤖 **AI-Powered Generation**: Create slides on any topic
- 🎨 **Customizable Themes**: Multiple themes and styling options
- 💾 **Persistent Storage**: SQLite database with async operations
- ⚡ **Fast Caching**: In-memory caching for quick responses
- 📊 **PPTX Export**: Download presentations as PowerPoint files
- 🔧 **Modular Design**: Easy to swap implementations
- 📚 **Auto Documentation**: Interactive API docs with Swagger

## Quick Start

### 1. Clone & Setup
```bash
git clone <repository-url>
cd slide-generator
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Setup
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Run the API
```bash
python -m app.main
```

Visit `http://localhost:8000/docs` for interactive API documentation.

## API Endpoints

### Presentations
- `POST /api/v1/presentations` - Create presentation
- `GET /api/v1/presentations/{id}` - Get presentation
- `GET /api/v1/presentations` - List presentations
- `DELETE /api/v1/presentations/{id}` - Delete presentation
- `GET /api/v1/presentations/{id}/download` - Download PPTX
- `POST /api/v1/presentations/{id}/configure` - Update configuration

### System
- `GET /` - Health check
- `GET /api/v1/cache/stats` - Cache statistics
- `POST /api/v1/cache/clear` - Clear cache
- `GET /api/v1/llm/status` - LLM service status

## Example Usage

### Create a Presentation
```bash
curl -X POST "http://localhost:8000/api/v1/presentations" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Machine Learning Basics",
    "num_slides": 5,
    "custom_content": "Focus on practical applications"
  }'
```

### Configure Presentation
```bash
curl -X POST "http://localhost:8000/api/v1/presentations/{id}/configure" \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "modern",
    "aspect_ratio": "16:9",
    "colors": {
      "primary": "#2E86AB",
      "secondary": "#A23B72"
    }
  }'
```

## Architecture

### Modular Design
- **Interfaces**: Abstract contracts for all services
- **Implementations**: Pluggable service implementations
- **Factory Pattern**: Easy service swapping
- **Dependency Injection**: Clean separation of concerns

### Services
- **Storage**: SQLite database with async operations
- **Cache**: In-memory caching with TTL
- **LLM**: OpenAI integration (with dummy fallback)
- **Generator**: Slide generation and PPTX creation

### Database Schema
- **Presentations**: Metadata, theme, configuration
- **Slides**: Content, type, order, citations

## Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `DATABASE_URL` | Database connection | `sqlite:///./slide_generator.db` |
| `API_HOST` | Server host | `0.0.0.0` |
| `API_PORT` | Server port | `8000` |

See [Environment Setup Guide](docs/ENVIRONMENT_SETUP.md) for detailed configuration.

## Development

### Project Structure
```
app/
├── apis/           # API routes
├── config/         # Configuration
├── interfaces/     # Abstract interfaces
├── middleware/     # Rate limiting, auth
├── models/         # Data models
├── services/       # Business logic
│   └── impl/      # Service implementations
└── main.py        # Application entry
```

### Testing
```bash
pytest tests/ -v
```

### Adding New Services
1. Implement the interface in `app/interfaces/`
2. Create implementation in `app/services/impl/`
3. Register in `app/services/factory.py`

## License

MIT License - see LICENSE file for details.


