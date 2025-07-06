# Test Suite Documentation

This document describes the comprehensive test suite for the Slide Generator API.

## Test Structure

The test suite is organized into modular components:

### 1. Configuration (`conftest.py`)
- **Purpose**: Centralized test configuration and fixtures
- **Key Features**:
  - Database session management for testing
  - Mock service setup
  - Sample data fixtures
  - Test client configuration

### 2. API Endpoints (`test_api_endpoints.py`)
- **Purpose**: Test all API endpoints and their behavior
- **Coverage**:
  - Health check endpoint
  - Authentication middleware
  - Presentation CRUD operations
  - Aspect ratio configuration
  - System management endpoints
  - Input validation

### 3. Middleware (`test_middleware.py`)
- **Purpose**: Test middleware components
- **Coverage**:
  - Rate limiting functionality
  - Authentication middleware
  - Concurrency control
  - Error handling
  - Header management

### 4. Services (`test_services.py`)
- **Purpose**: Test service layer components
- **Coverage**:
  - Dummy LLM service
  - Cache service
  - Database storage service
  - Slide generator service
  - Service factory

### 5. Models (`test_models.py`)
- **Purpose**: Test data models and validation
- **Coverage**:
  - Slide model
  - Presentation model
  - Presentation configuration
  - Database models
  - Theme configuration
  - Aspect ratio configuration

## Running Tests

### Prerequisites
```bash
pip install pytest pytest-asyncio
```

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# API tests only
pytest tests/test_api_endpoints.py

# Middleware tests only
pytest tests/test_middleware.py

# Service tests only
pytest tests/test_services.py

# Model tests only
pytest tests/test_models.py
```

### Run with Coverage
```bash
pip install pytest-cov
pytest --cov=app --cov-report=html
```

### Run with Verbose Output
```bash
pytest -v
```

## Test Categories

### Unit Tests
- Individual component testing
- Mock dependencies
- Fast execution
- Isolated testing

### Integration Tests
- Component interaction testing
- Database integration
- API endpoint testing
- Real service interaction

### Functional Tests
- End-to-end workflow testing
- User scenario testing
- Business logic validation

## Key Test Features

### 1. Authentication Testing
- API key validation
- Bearer token support
- X-API-Key header support
- Unauthorized access handling

### 2. Rate Limiting Testing
- Request counting
- Limit enforcement
- Header response validation
- IP address extraction

### 3. Concurrency Testing
- Global semaphore management
- Per-user limits
- Resource contention handling
- Statistics tracking

### 4. Aspect Ratio Testing
- Standard ratio validation
- Custom dimension validation
- Configuration retrieval
- Limit enforcement

### 5. Theme Testing
- Theme configuration validation
- Color scheme testing
- Font configuration
- Default fallbacks

## Test Data Management

### Fixtures
- Sample presentation data
- Configuration templates
- Mock service instances
- Database session management

### Cleanup
- Automatic database cleanup
- Cache clearing
- Temporary file removal
- Resource cleanup

## Best Practices

### 1. Test Isolation
- Each test is independent
- No shared state between tests
- Proper setup and teardown

### 2. Mocking Strategy
- External dependencies mocked
- Database operations isolated
- LLM responses controlled
- Cache behavior predictable

### 3. Assertion Quality
- Specific assertions
- Meaningful error messages
- Edge case coverage
- Boundary testing

### 4. Performance
- Fast test execution
- Minimal external dependencies
- Efficient resource usage
- Parallel execution support

## Continuous Integration

The test suite is designed to run in CI/CD environments:

### GitHub Actions
```yaml
- name: Run Tests
  run: |
    pip install -r requirements.txt
    pytest --cov=app --cov-report=xml
```

### Local Development
```bash
# Run tests before commit
pytest

# Run specific test file
pytest tests/test_api_endpoints.py::TestPresentations::test_create_presentation

# Run tests with specific marker
pytest -m "not slow"
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure app directory is in Python path
   - Check virtual environment activation
   - Verify package installation

2. **Database Errors**
   - Check test database configuration
   - Ensure migrations are applied
   - Verify connection settings

3. **Mock Issues**
   - Check mock setup in fixtures
   - Verify import paths
   - Ensure proper patching

### Debug Mode
```bash
# Run with debug output
pytest -s -v

# Run single test with debug
pytest -s -v tests/test_api_endpoints.py::TestPresentations::test_create_presentation
```

## Coverage Goals

- **API Endpoints**: 100%
- **Middleware**: 95%+
- **Services**: 90%+
- **Models**: 95%+
- **Overall**: 90%+

## Future Enhancements

1. **Performance Testing**
   - Load testing scenarios
   - Stress testing
   - Memory usage monitoring

2. **Security Testing**
   - Penetration testing
   - Vulnerability scanning
   - Security best practices validation

3. **Accessibility Testing**
   - WCAG compliance
   - Screen reader compatibility
   - Keyboard navigation

4. **Internationalization Testing**
   - Multi-language support
   - Locale-specific formatting
   - Character encoding validation 