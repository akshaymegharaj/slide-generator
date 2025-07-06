# Slide Generator Architecture

## Overview
The Slide Generator follows a modular, production-ready architecture with clear separation of concerns and easy implementation swapping.

## Directory Structure

```
app/
├── interfaces/           # Abstract base classes (contracts)
│   ├── cache.py         # CacheInterface
│   ├── llm.py           # LLMInterface  
│   └── storage.py       # StorageInterface
├── services/            # Production-ready implementations
│   ├── cache.py         # In-memory cache implementation
│   ├── database_storage.py  # SQLite storage implementation
│   ├── dummy_llm.py     # Dummy LLM for testing/development
│   ├── factory.py       # Service factory for dependency injection
│   ├── slide_generator.py   # Main slide generation logic
│   ├── storage.py       # Storage service wrapper
│   └── impl/            # Service implementations
│       ├── openai_llm.py # OpenAI GPT implementation
│       └── redis_cache.py # Redis cache implementation
├── models/              # Data models
├── main.py              # Admin API endpoints only
├── apis/                # API routes
│   ├── system.py        # System endpoints (health, cache, LLM, concurrency)
│   ├── config.py        # Configuration endpoints (aspect ratios)
│   └── presentation_api.py  # Presentation-related endpoints
└── settings.py          # Configuration (gitignored)
```

## Architecture Principles

### 1. Interface Segregation
- **Interfaces** (`app/interfaces/`) define contracts that implementations must follow
- Each interface focuses on a single responsibility
- Easy to swap implementations without changing business logic

### 2. Production vs Implementations
- **Services** (`app/services/`) contain production-ready implementations
- **Impl** (`app/services/impl/`) contain additional service implementations
- Clear separation prevents confusion about what's production-ready

### 3. Dependency Injection
- **Factory Pattern** (`app/services/factory.py`) manages service instances
- Easy to swap implementations at runtime
- Centralized service management

### 4. Modular API Design
- **Admin endpoints** (`app/main.py`) - health checks, cache management, LLM switching
- **Business endpoints** (`app/apis/presentation_api.py`) - presentation CRUD operations
- **System endpoints** (`app/apis/system.py`) - health check, cache, LLM, concurrency
- **Configuration endpoints** (`app/apis/config.py`) - aspect ratios and config options
- Clear separation of concerns

## Service Implementations

### LLM Services
- **DummyLLM** (`app/services/dummy_llm.py`) - Production-ready dummy implementation for testing
- **OpenAILLM** (`app/services/impl/openai_llm.py`) - OpenAI GPT implementation

### Cache Services  
- **CacheService** (`app/services/cache.py`) - Production in-memory cache
- **RedisCacheService** (`app/services/impl/redis_cache.py`) - Redis implementation

### Storage Services
- **DatabaseStorage** (`app/services/database_storage.py`) - Production SQLite storage
- **StorageService** (`app/services/storage.py`) - Storage service wrapper

## Usage Examples

### Switching LLM Implementation
```python
from app.services.factory import service_factory
from app.services.impl.openai_llm import OpenAILLM

# Switch to OpenAI
openai_llm = OpenAILLM(api_key="your-key")
service_factory.set_llm_service(openai_llm)
```

### Using Dummy LLM (Default)
```python
from app.services.factory import service_factory
from app.services.dummy_llm import DummyLLM

# Switch to dummy (default)
dummy_llm = DummyLLM()
service_factory.set_llm_service(dummy_llm)
```

## Benefits

1. **Modularity** - Easy to add new implementations
2. **Testability** - Clear interfaces make testing straightforward
3. **Maintainability** - Separation of concerns keeps code organized
4. **Scalability** - Easy to swap implementations as needs grow
5. **Clarity** - Clear distinction between production and example code

## Configuration

- **Settings** (`app/settings.py`) - Contains API keys and configuration
- **Gitignored** - Prevents accidental commit of secrets
- **Environment Variables** - Can override settings via environment 