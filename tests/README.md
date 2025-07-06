# Tests

This directory contains test files for the Slide Generator API.

## Test Files

- **`test_api.py`** - API endpoint tests covering presentation creation, retrieval, and download functionality

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

## Test Coverage

The tests cover:
- Presentation creation with different parameters
- Presentation retrieval and listing
- Download functionality
- Error handling and edge cases
- API authentication

## Test Configuration

- **`pytest.ini`** - Pytest configuration file in the root directory
- Tests use the test database and dummy LLM for consistent results
- API key authentication is tested with valid and invalid keys

## Adding Tests

When adding new features:
1. Create test functions in the appropriate test file
2. Test both success and failure scenarios
3. Include edge cases and error conditions
4. Ensure tests are independent and can run in any order

## Test Data

Tests use:
- Mock data for consistent results
- Temporary test database
- Dummy LLM service to avoid external API calls
- Sample presentation data for validation 