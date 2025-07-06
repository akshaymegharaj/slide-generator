# Slide Generator API

Generate customizable presentation slides using AI. Built with FastAPI, SQLite, and a modular, swappable architecture.

## Features
- AI-powered slide generation
- Customizable themes & aspect ratios
- Persistent SQLite storage
- Fast in-memory caching
- PPTX export
- Modular, pluggable design
- Interactive API docs (Swagger)

## Quick Start
```bash
git clone <repository-url>
cd slide-generator
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Add your OpenAI API key
```

## Run the API
```bash
python -m app.main
# or
uvicorn app.main:app --reload
```
Visit [localhost:8000/docs](http://localhost:8000/docs) for interactive API docs.

## Documentation
📚 **Detailed documentation** is available in the [`docs/`](docs/) folder:
- [API Documentation](docs/API_DOCUMENTATION.md) - Complete API reference
- [Architecture Guide](docs/ARCHITECTURE.md) - System design and patterns
- [Environment Setup](docs/ENVIRONMENT_SETUP.md) - Configuration details
- [Middleware Guide](docs/MIDDLEWARE_GUIDE.md) - Auth, rate limiting, etc.
- [Setup Instructions](docs/SETUP_INSTRUCTIONS.md) - Step-by-step guide

## Key API Endpoints
- `POST /api/v1/presentations` – Create presentation
- `GET /api/v1/presentations/{id}` – Get presentation
- `GET /api/v1/presentations` – List presentations
- `GET /api/v1/presentations/{id}/download` – Download PPTX
- `POST /api/v1/presentations/{id}/configure` – Update config

## Example: Create a Presentation
```bash
curl -X POST "http://localhost:8000/api/v1/presentations" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Machine Learning Basics", "num_slides": 5}'
```

## Modular Architecture
- **Interfaces**: Abstract contracts for LLM, cache, storage
- **Implementations**: Pluggable (OpenAI, dummy LLM, Redis, etc.)
- **Factory pattern**: Easy to swap components

## Project Structure
```
app/
  apis/         # API routes
  config/       # Config & themes
  interfaces/   # Abstract interfaces
  middleware/   # Auth, rate limiting
  models/       # Data models
  services/     # Logic & implementations
  main.py       # Entry point
```

## Configuration
- `.env` for secrets and API keys
- See `docs/ENVIRONMENT_SETUP.md` for details

## Testing
```bash
pytest tests/ -v
```

## License
MIT


