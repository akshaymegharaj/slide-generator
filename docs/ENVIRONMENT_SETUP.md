# Environment Setup Guide

This guide explains how to set up environment variables for the Slide Generator API.

## Quick Setup

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the .env file with your actual values:**
   ```bash
   # Edit .env file with your OpenAI API key
   nano .env
   ```

3. **Replace the placeholder with your actual OpenAI API key:**
   ```
   OPENAI_API_KEY=sk-your-actual-openai-api-key-here
   ```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key for content generation | `sk-proj-...` |

### Optional Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./slide_generator.db` | `sqlite:///./my_db.db` |
| `API_HOST` | Host to bind the API server | `0.0.0.0` | `127.0.0.1` |
| `API_PORT` | Port to bind the API server | `8000` | `8080` |
| `CACHE_TTL` | Cache time-to-live in seconds | `3600` | `1800` |
| `RATE_LIMIT_REQUESTS` | Maximum requests per window | `100` | `50` |
| `RATE_LIMIT_WINDOW` | Rate limit window in seconds | `3600` | `1800` |
| `MAX_CONCURRENT_REQUESTS` | Maximum concurrent requests per user | `5` | `10` |

## Security Notes

- **Never commit your .env file to git** - it's already in .gitignore
- **Keep your API keys secure** - don't share them in code or documentation
- **Use different API keys for development and production**
- **Rotate your API keys regularly** for security

## Development vs Production

### Development
- Use a `.env` file for local development
- Set `API_HOST=127.0.0.1` for local-only access
- Use test API keys if available

### Production
- Set environment variables directly on your server/container
- Use strong, production API keys
- Set appropriate rate limits and concurrency controls
- Use secure database connections

## Troubleshooting

### API Key Issues
If you get authentication errors:
1. Verify your OpenAI API key is correct
2. Check that the key has sufficient credits
3. Ensure the key has the required permissions

### Environment Variable Not Loading
If environment variables aren't being loaded:
1. Check that `.env` file exists in the project root
2. Verify `python-dotenv` is installed: `pip install python-dotenv`
3. Restart your application after making changes

### Database Issues
If you have database connection issues:
1. Check the `DATABASE_URL` format
2. Ensure the database directory is writable
3. Verify SQLite is available (included with Python)

## Example .env File

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-actual-key-here

# Database Configuration
DATABASE_URL=sqlite:///./slide_generator.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Cache Configuration
CACHE_TTL=3600

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Concurrency Control
MAX_CONCURRENT_REQUESTS=5
``` 