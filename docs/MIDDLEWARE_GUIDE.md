# Middleware Guide for Slide Generator API

This guide explains how to use the rate limiting, authentication, and concurrency control middleware implemented in the Slide Generator API.

## Table of Contents

1. [Rate Limiting](#rate-limiting)
2. [Authentication](#authentication)
3. [Concurrency Control](#concurrency-control)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [Testing](#testing)

## Rate Limiting

The rate limiting middleware prevents abuse by limiting the number of requests per client IP address.

### Features

- **Per-minute limits**: Configurable requests per minute (default: 60)
- **Per-hour limits**: Configurable requests per hour (default: 1000)
- **IP-based tracking**: Uses client IP address for identification
- **Proxy support**: Handles X-Forwarded-For and X-Real-IP headers
- **Cache-based**: Uses the existing cache system for storage

### Configuration

Set environment variables to configure rate limits:

```bash
# Rate limiting configuration
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
RATE_LIMIT_CACHE_TTL=3600
```

### Response Headers

Rate limiting adds the following headers to responses:

- `X-RateLimit-Minute-Limit`: Maximum requests per minute
- `X-RateLimit-Minute-Remaining`: Remaining requests in current minute
- `X-RateLimit-Hour-Limit`: Maximum requests per hour
- `X-RateLimit-Hour-Remaining`: Remaining requests in current hour

### Rate Limit Exceeded Response

When rate limits are exceeded, the API returns:

```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Limit: 60 per minute",
  "retry_after": 60
}
```

With HTTP status code `429` and `Retry-After` header.

## Authentication

The authentication middleware provides API key-based authentication.

### Features

- **API Key support**: Bearer token or X-API-Key header
- **Environment-based configuration**: Load API keys from environment variables
- **Optional authentication**: Can be disabled for development
- **User identification**: Extracts user information from API keys
- **Skip paths**: Certain endpoints bypass authentication

### Configuration

Set environment variables to configure authentication:

```bash
# Authentication configuration
API_KEYS=key1,key2,key3
AUTH_REQUIRED=false  # Set to true to require authentication
```

### API Key Usage

#### Bearer Token
```bash
curl -H "Authorization: Bearer your-api-key" \
     http://localhost:8000/api/v1/presentations
```

#### X-API-Key Header
```bash
curl -H "X-API-Key: your-api-key" \
     http://localhost:8000/api/v1/presentations
```

### Authentication-Free Endpoints

The following endpoints bypass authentication:

- `/` - Health check
- `/docs` - API documentation
- `/openapi.json` - OpenAPI schema
- `/api/v1/cache/stats` - Cache statistics
- `/api/v1/llm/status` - LLM status

### Response Headers

Authentication adds the following header to responses:

- `X-User-ID`: User identifier (for authenticated requests)

### Authentication Error Response

When authentication fails, the API returns:

```json
{
  "error": "Unauthorized",
  "message": "API key required"
}
```

With HTTP status code `401` and `WWW-Authenticate: Bearer` header.

## Concurrency Control

The concurrency control middleware manages simultaneous requests to prevent resource exhaustion.

### Features

- **Global limits**: Maximum concurrent requests across all users
- **Per-user limits**: Maximum concurrent requests per user
- **Resource-intensive operations**: Applied to CPU/memory intensive endpoints
- **Semaphore-based**: Uses asyncio semaphores for efficient control
- **User identification**: Uses authentication or IP address

### Configuration

Set environment variables to configure concurrency:

```bash
# Concurrency configuration
MAX_CONCURRENT_REQUESTS=100
MAX_CONCURRENT_PER_USER=10
```

### Controlled Endpoints

Concurrency control is applied to:

- `POST /api/v1/presentations` - Create presentations
- `GET /api/v1/presentations/{id}/download` - Download presentations

### Response Headers

Concurrency control adds the following headers to responses:

- `X-Concurrency-User-ID`: User identifier
- `X-Concurrency-Global-Limit`: Global concurrent request limit
- `X-Concurrency-User-Limit`: Per-user concurrent request limit

### Concurrency Statistics

Get current concurrency statistics:

```bash
curl http://localhost:8000/api/v1/concurrency/stats
```

Response:
```json
{
  "global_semaphore": {
    "value": 95,
    "locked": false
  },
  "user_semaphores": {
    "user_123": {
      "value": 8,
      "locked": false
    }
  },
  "limits": {
    "max_concurrent_requests": 100,
    "max_concurrent_per_user": 10
  }
}
```

### Concurrency Error Response

When concurrency limits are exceeded, the API returns:

```json
{
  "error": "Service temporarily unavailable",
  "message": "Too many concurrent requests. Please try again later."
}
```

With HTTP status code `503`.

## Configuration

### Environment Variables

All middleware configuration is done through environment variables:

```bash
# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
RATE_LIMIT_CACHE_TTL=3600

# Authentication
API_KEYS=key1,key2,key3
AUTH_REQUIRED=false

# Concurrency
MAX_CONCURRENT_REQUESTS=100
MAX_CONCURRENT_PER_USER=10
```

### Configuration API

Get current middleware configuration:

```python
from app.config.middleware import MiddlewareConfig

# Get all configuration
config = MiddlewareConfig.get_all_config()

# Get specific configuration
rate_config = MiddlewareConfig.get_rate_limit_config()
auth_config = MiddlewareConfig.get_auth_config()
concurrency_config = MiddlewareConfig.get_concurrency_config()
```

## Usage Examples

### Basic Usage

1. **Start the server with middleware enabled**:
   ```bash
   python -m app.main
   ```

2. **Make authenticated requests**:
   ```bash
   # Set API key
   export API_KEY="your-secret-key"
   
   # Create presentation with authentication
   curl -X POST "http://localhost:8000/api/v1/presentations" \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{
          "topic": "Machine Learning Basics",
          "num_slides": 5
        }'
   ```

3. **Check rate limits**:
   ```bash
   # Response will include rate limit headers
   curl -I "http://localhost:8000/api/v1/presentations"
   ```

### Advanced Usage

1. **Custom rate limits**:
   ```bash
   # Set custom rate limits
   export RATE_LIMIT_PER_MINUTE=30
   export RATE_LIMIT_PER_HOUR=500
   python -m app.main
   ```

2. **Multiple API keys**:
   ```bash
   # Set multiple API keys
   export API_KEYS="key1,key2,key3,key4"
   python -m app.main
   ```

3. **Strict authentication**:
   ```bash
   # Require authentication for all endpoints
   export AUTH_REQUIRED=true
   export API_KEYS="your-secret-key"
   python -m app.main
   ```

### Development vs Production

#### Development Configuration
```bash
# Development - relaxed limits, no auth required
RATE_LIMIT_PER_MINUTE=1000
RATE_LIMIT_PER_HOUR=10000
AUTH_REQUIRED=false
MAX_CONCURRENT_REQUESTS=200
MAX_CONCURRENT_PER_USER=50
```

#### Production Configuration
```bash
# Production - strict limits, auth required
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_PER_HOUR=500
AUTH_REQUIRED=true
API_KEYS="prod-key-1,prod-key-2,prod-key-3"
MAX_CONCURRENT_REQUESTS=50
MAX_CONCURRENT_PER_USER=5
```

## Testing

### Run Middleware Tests

```bash
# Run all middleware tests
pytest tests/test_middleware.py -v

# Run specific test classes
pytest tests/test_middleware.py::TestRateLimiter -v
pytest tests/test_middleware.py::TestAuthMiddleware -v
pytest tests/test_middleware.py::TestConcurrencyController -v
```

### Manual Testing

1. **Test rate limiting**:
   ```bash
   # Make many requests quickly to trigger rate limit
   for i in {1..70}; do
     curl -s "http://localhost:8000/api/v1/presentations" > /dev/null
     echo "Request $i"
   done
   ```

2. **Test authentication**:
   ```bash
   # Test without API key (should fail if AUTH_REQUIRED=true)
   curl "http://localhost:8000/api/v1/presentations"
   
   # Test with invalid API key
   curl -H "Authorization: Bearer invalid-key" \
        "http://localhost:8000/api/v1/presentations"
   
   # Test with valid API key
   curl -H "Authorization: Bearer your-valid-key" \
        "http://localhost:8000/api/v1/presentations"
   ```

3. **Test concurrency**:
   ```bash
   # Make concurrent requests
   for i in {1..20}; do
     curl -X POST "http://localhost:8000/api/v1/presentations" \
          -H "Content-Type: application/json" \
          -d '{"topic": "Test $i", "num_slides": 3}' &
   done
   wait
   ```

### Monitoring

1. **Check cache statistics**:
   ```bash
   curl "http://localhost:8000/api/v1/cache/stats"
   ```

2. **Check concurrency statistics**:
   ```bash
   curl "http://localhost:8000/api/v1/concurrency/stats"
   ```

3. **Check LLM status**:
   ```bash
   curl "http://localhost:8000/api/v1/llm/status"
   ```

## Troubleshooting

### Common Issues

1. **Rate limit errors (429)**:
   - Reduce request frequency
   - Increase rate limits in configuration
   - Check if multiple clients are using the same IP

2. **Authentication errors (401)**:
   - Verify API key is correct
   - Check if API key is in the API_KEYS environment variable
   - Ensure AUTH_REQUIRED is set correctly

3. **Concurrency errors (503)**:
   - Reduce concurrent requests
   - Increase concurrency limits
   - Check server resources

4. **Cache issues**:
   - Clear cache: `curl -X POST "http://localhost:8000/api/v1/cache/clear"`
   - Check cache statistics
   - Verify cache configuration

### Debug Mode

Enable debug logging by setting environment variables:

```bash
export PYTHONPATH=.
export LOG_LEVEL=DEBUG
python -m app.main
```

### Performance Monitoring

Monitor middleware performance:

```bash
# Check response times with middleware
time curl "http://localhost:8000/api/v1/presentations"

# Monitor memory usage
ps aux | grep python

# Check cache hit rates
curl "http://localhost:8000/api/v1/cache/stats"
```

## Security Considerations

1. **API Key Security**:
   - Use strong, random API keys
   - Rotate API keys regularly
   - Never commit API keys to version control
   - Use environment variables or secure key management

2. **Rate Limiting**:
   - Set appropriate limits for your use case
   - Monitor for abuse patterns
   - Consider IP whitelisting for trusted clients

3. **Concurrency Control**:
   - Balance between performance and resource usage
   - Monitor server resources
   - Adjust limits based on server capacity

4. **Logging and Monitoring**:
   - Log authentication attempts
   - Monitor rate limit violations
   - Track concurrency usage patterns
   - Set up alerts for unusual activity 