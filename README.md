# Slide Generator API

A modern, scalable API for generating customizable presentation slides on any topic. Built with FastAPI, SQLModel, and in-memory caching.

## Features

- **AI-Powered Slide Generation**: Generate presentation slides on any topic
- **Persistent Storage**: SQLite database with SQLModel for reliable data persistence
- **In-Memory Caching**: Fast response times with intelligent caching
- **Customizable Themes**: Multiple presentation themes and styling options
- **PPTX Export**: Download presentations as PowerPoint files
- **RESTful API**: Clean, documented API endpoints
- **Async Support**: Full async/await support for high performance

## Architecture

### Modular Design
The application is built with a **modular architecture** that allows seamless swapping of implementations:

- **Interface-Based Design**: All services implement abstract interfaces
- **Dependency Injection**: Services are injected through a factory pattern
- **Loose Coupling**: Components can be replaced without changing the main application
- **Easy Testing**: Mock implementations can be easily swapped in

### Service Interfaces
- **StorageInterface**: Abstract storage operations (SQLite, PostgreSQL, etc.)
- **CacheInterface**: Abstract caching operations (In-Memory, Redis, etc.)
- **LLMInterface**: Abstract LLM operations (Dummy, OpenAI, Anthropic, etc.)

### Database Layer
- **SQLModel**: Modern Python library that combines SQLAlchemy and Pydantic
- **SQLite**: Lightweight, serverless database for easy deployment
- **Async Support**: Full async database operations for better performance
- **Swappable**: Can easily switch to PostgreSQL, MySQL, etc.

### Caching Layer
- **In-Memory Caching**: Fast access to frequently requested data
- **TTL (Time-To-Live)**: Automatic cache expiration to prevent stale data
- **Multiple Cache Types**:
  - Presentation cache (1 hour TTL)
  - Slide generation cache (30 minutes TTL)
  - API response cache (15 minutes TTL)
- **Swappable**: Can easily switch to Redis, Memcached, etc.

### LLM Layer
- **Dummy LLM**: Placeholder implementation for development/testing
- **OpenAI Integration**: Ready-to-use OpenAI implementation
- **Swappable**: Can easily switch to Anthropic, Google, etc.

### API Layer
- **FastAPI**: Modern, fast web framework for building APIs
- **Automatic Documentation**: Interactive API docs with Swagger UI
- **Type Safety**: Full type hints and validation
- **Dependency Injection**: Clean separation of concerns

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd slide-generator
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env file and add your OpenAI API key
   ```

5. **Set up the database**:
   ```bash
   python -m app.migrations
   ```

## Usage

### Starting the Server

```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

### API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

### Key Endpoints

#### Presentations
- `POST /api/v1/presentations` - Create a new presentation
- `GET /api/v1/presentations/{id}` - Get presentation details
- `GET /api/v1/presentations` - List all presentations
- `GET /api/v1/presentations/search/{topic}` - Search presentations by topic
- `DELETE /api/v1/presentations/{id}` - Delete a presentation
- `GET /api/v1/presentations/{id}/download` - Download as PPTX
- `POST /api/v1/presentations/{id}/configure` - Update presentation configuration

#### Cache Management
- `GET /api/v1/cache/stats` - Get cache statistics
- `POST /api/v1/cache/clear` - Clear all caches

### Example Usage

#### Create a Presentation
```bash
curl -X POST "http://localhost:8000/api/v1/presentations" \
     -H "Content-Type: application/json" \
     -d '{
       "topic": "Machine Learning Basics",
       "num_slides": 5,
       "custom_content": "Focus on practical applications"
     }'
```

#### Get Cache Statistics
```bash
curl "http://localhost:8000/api/v1/cache/stats"
```

### Modular Architecture Examples

#### Swapping LLM Providers
```python
from app.services.factory import service_factory
from app.services.impl.openai_llm import OpenAILLM

# Swap to OpenAI LLM
openai_llm = OpenAILLM(api_key="your-api-key")
service_factory.set_llm_service(openai_llm)

# The application now uses OpenAI for content generation
```

#### Swapping Cache Backends
```python
from app.services.examples.redis_cache import RedisCacheService

# Swap to Redis cache
redis_cache = RedisCacheService(redis_url="redis://localhost:6379")
service_factory.set_cache_service(redis_cache)

# The application now uses Redis for caching
```

#### Creating Custom Implementations
```python
from app.interfaces.cache import CacheInterface

class CustomCache(CacheInterface):
    def __init__(self):
        self.data = {}
    
    def get_presentation(self, presentation_id: str):
        return self.data.get(f"presentation:{presentation_id}")
    
    # Implement other required methods...
    
# Use custom cache
service_factory.set_cache_service(CustomCache())
```

#### Running the Modular Demo
```bash
python demo_modular_architecture.py
```

## Database Schema

### Presentations Table
- `id` (String, Primary Key): Unique presentation identifier
- `topic` (String): Presentation topic
- `num_slides` (Integer): Number of slides
- `custom_content` (String, Optional): Custom content instructions
- `theme` (Enum): Presentation theme
- `font` (String): Font family
- `colors` (JSON): Color scheme
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

### Slides Table
- `id` (Integer, Primary Key): Unique slide identifier
- `presentation_id` (String, Foreign Key): Reference to presentation
- `slide_type` (Enum): Type of slide
- `title` (String): Slide title
- `content` (JSON): Slide content as list
- `image_suggestion` (String, Optional): Suggested image
- `citations` (JSON): List of citations
- `slide_order` (Integer): Slide order in presentation
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

## Caching Strategy

### Cache Types and TTLs
1. **Presentation Cache** (1 hour TTL, max 100 items)
   - Caches complete presentation objects
   - Reduces database queries for frequently accessed presentations

2. **Slide Generation Cache** (30 minutes TTL, max 200 items)
   - Caches slide generation results
   - Prevents regenerating identical slides

3. **API Response Cache** (15 minutes TTL, max 500 items)
   - Caches API endpoint responses
   - Improves response times for repeated requests

### Cache Keys
- **Presentation Cache**: Uses presentation ID
- **Slide Generation Cache**: Uses hash of generation parameters
- **API Response Cache**: Uses hash of endpoint and parameters

## Development

### Running Tests
```bash
pytest tests/
```

### Database Migrations
```bash
# Run migrations
python -m app.migrations

# Reset database
python -m app.migrations reset
```

### Code Structure
```
app/
├── __init__.py
├── main.py              # FastAPI application
├── database.py          # Database configuration
├── migrations.py        # Database migrations
├── interfaces/          # Abstract service interfaces
│   ├── __init__.py
│   ├── storage.py       # Storage interface
│   ├── cache.py         # Cache interface
│   └── llm.py           # LLM interface
├── models/
│   ├── __init__.py
│   ├── presentation.py  # Pydantic models
│   └── database.py      # SQLModel database models
├── services/
│   ├── __init__.py
│   ├── factory.py       # Service factory for DI
│   ├── cache.py         # In-memory cache implementation
│   ├── database_storage.py  # SQLite storage implementation
│   ├── slide_generator.py   # Slide generation service
│   ├── llm/
│   │   └── dummy_llm.py     # Dummy LLM implementation
│   └── examples/        # Example implementations
│       ├── redis_cache.py   # Redis cache example
│       └── openai_llm.py    # OpenAI LLM example
```

## Performance Considerations

### Caching Benefits
- **Reduced Database Load**: Frequently accessed data served from memory
- **Faster Response Times**: Cache hits return data immediately
- **Scalability**: Reduces resource usage under high load

### Database Optimization
- **Indexed Queries**: Foreign keys and frequently searched fields are indexed
- **Async Operations**: Non-blocking database operations
- **Connection Pooling**: Efficient database connection management

### Memory Management
- **TTL Expiration**: Automatic cache cleanup prevents memory bloat
- **Size Limits**: Maximum cache sizes prevent unlimited memory growth
- **LRU Eviction**: Least recently used items evicted when limits reached

## Deployment

### Environment Variables
- `DATABASE_URL`: SQLite database URL (default: `sqlite+aiosqlite:///./slide_generator.db`)

### Production Considerations
- **Database**: Consider using PostgreSQL for production
- **Caching**: Use Redis for distributed caching
- **Security**: Implement authentication and rate limiting
- **Monitoring**: Add logging and metrics collection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.


