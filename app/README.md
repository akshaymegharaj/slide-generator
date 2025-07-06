# App Directory Structure

This directory contains the core application code for the Slide Generator API, organized using a modular, layered architecture.

## Directory Overview

```
app/
├── apis/           # API route handlers and endpoints
├── config/         # Configuration, themes, and settings
├── database/       # Database connection and migrations
├── interfaces/     # Abstract interfaces and contracts
├── middleware/     # Authentication, rate limiting, and other middleware
├── models/         # Data models and schemas
├── services/       # Business logic and service implementations
└── main.py         # Application entry point
```

## Detailed Structure

### `apis/` - API Layer
- **`presentation_api.py`** - Presentation-related endpoints (CRUD operations, download, configure)
- **`system.py`** - System health and status endpoints
- **`__init__.py`** - Package initialization

**Purpose**: Handles HTTP requests, input validation, and response formatting. Separates API logic from business logic.

### `config/` - Configuration Management
- **`aspect_ratios.py`** - Available slide aspect ratios and dimensions
- **`middleware.py`** - Middleware configuration settings
- **`themes.py`** - Theme definitions, colors, and fonts
- **`__init__.py`** - Package initialization

**Purpose**: Centralizes all configuration constants, theme definitions, and application settings.

### `database/` - Data Persistence
- **`connection.py`** - Database connection setup and session management
- **`migrations.py`** - Database schema migrations
- **`__init__.py`** - Package initialization

**Purpose**: Manages database connections, sessions, and schema evolution.

### `interfaces/` - Abstract Contracts
- **`cache.py`** - Cache interface definition
- **`llm.py`** - Language model interface definition
- **`storage.py`** - Storage interface definition
- **`__init__.py`** - Package initialization

**Purpose**: Defines abstract interfaces that allow for pluggable implementations. Enables easy swapping of components.

### `middleware/` - Request Processing
- **`auth.py`** - API key authentication middleware
- **`concurrency.py`** - Request concurrency management
- **`rate_limiter.py`** - Rate limiting implementation
- **`__init__.py`** - Package initialization

**Purpose**: Handles cross-cutting concerns like authentication, rate limiting, and request processing.

### `models/` - Data Models
- **`database.py`** - SQLAlchemy database models
- **`presentation.py`** - Pydantic models for API requests/responses
- **`__init__.py`** - Package initialization

**Purpose**: Defines data structures for both database persistence and API communication.

### `services/` - Business Logic
- **`cache.py`** - Cache service implementation
- **`database_storage.py`** - Database storage implementation
- **`dummy_llm.py`** - Dummy LLM for testing
- **`factory.py`** - Service factory for dependency injection
- **`slide_generator.py`** - Core slide generation logic
- **`storage.py`** - Storage service implementation
- **`impl/`** - Concrete implementations
  - **`openai_llm/`** - OpenAI LLM implementation
    - **`prompts/`** - LLM prompt templates
    - **`constants.py`** - OpenAI-specific constants
    - **`openai_llm.py`** - OpenAI integration
  - **`redis_cache.py`** - Redis cache implementation
- **`__init__.py`** - Package initialization

**Purpose**: Contains all business logic, external service integrations, and core application functionality.

### `main.py` - Application Entry Point
- FastAPI application initialization
- Middleware registration
- Route registration
- Dependency injection setup

**Purpose**: Bootstraps the application and wires all components together.

## Architecture Principles

### 1. **Separation of Concerns**
- APIs handle HTTP concerns
- Services contain business logic
- Models define data structures
- Interfaces enable loose coupling

### 2. **Dependency Injection**
- Services are injected through the factory pattern
- Easy to swap implementations (e.g., OpenAI → Dummy LLM)
- Testable and maintainable code

### 3. **Interface Segregation**
- Clear contracts through abstract interfaces
- Multiple implementations possible
- Easy to extend with new providers

### 4. **Configuration Management**
- Centralized configuration
- Environment-specific settings
- Theme and aspect ratio definitions

### 5. **Middleware Pattern**
- Cross-cutting concerns separated
- Reusable authentication and rate limiting
- Clean request/response processing

## Key Design Patterns

- **Factory Pattern**: Service instantiation and dependency injection
- **Repository Pattern**: Data access abstraction through storage interfaces
- **Strategy Pattern**: Pluggable LLM and cache implementations
- **Middleware Pattern**: Request processing pipeline
- **Dependency Injection**: Loose coupling between components

## Adding New Features

1. **New API Endpoint**: Add to `apis/` directory
2. **New Service**: Implement interface in `services/` and add to factory
3. **New Model**: Add to `models/` directory
4. **New Configuration**: Add to `config/` directory
5. **New Middleware**: Add to `middleware/` directory

This structure ensures maintainability, testability, and extensibility of the Slide Generator API. 