# Slide Generator API - Setup Instructions

## 1. Prerequisites
- Python 3.9+
- pip (Python package manager)
- (Optional) Redis (if using Redis cache)

## 2. Clone the Repository
```bash
git clone <your-repo-url>
cd slide-generator
```

## 3. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## 4. Install Dependencies
```bash
pip install -r requirements.txt
```

## 5. Configure Environment Variables
Create a `.env` file or export variables in your shell. Example:
```env
# API Keys (comma-separated for multiple users)
API_KEYS=demo-api-key-12345,another-key-67890

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Concurrency
MAX_CONCURRENT_REQUESTS=100
MAX_CONCURRENT_PER_USER=10

# Authentication
AUTH_REQUIRED=true

# (Optional) OpenAI API Key
OPENAI_API_KEY=sk-...
```

## 6. Initialize the Database
```bash
python -m app.migrations
```

## 7. Run the Server
```bash
python -m app.main
```
- The API will be available at `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`

## 8. Run Tests
```bash
pytest
```

## 9. Demo & Examples
- See `demo_middleware.py` for a demo script.
- See `MIDDLEWARE_GUIDE.md` for middleware usage.

## 10. Postman Collection
- Import `postman_collection.json` into Postman to try all endpoints.

## 11. Sample Presentations
- Generated `.pptx` files are saved in the `output/` directory.

---

For more details, see `API_DOCUMENTATION.md` and `MIDDLEWARE_GUIDE.md`. 