"""
Slide Generator API - Main Application
"""
from fastapi import FastAPI
from app.settings import OPENAI_API_KEY

# Import services
from app.services.factory import service_factory
from app.services.slide_generator import SlideGenerator
from app.services.impl.openai_llm import OpenAILLM

# Import database
from app.database import create_db_and_tables

# Import middleware
from app.middleware import rate_limiter, auth_middleware, concurrency_controller

# Import API routes
from app.apis.system import router as system_router
from app.apis.presentation_api import router as presentation_router

app = FastAPI(
    title="Slide Generator API",
    description="Generate customizable presentation slides on any topic",
    version="1.0.0"
)

# Initialize services using factory
cache_service = service_factory.get_cache_service()
storage = service_factory.get_storage_service()

def configure_llm_service():
    """Configure LLM service based on settings file or environment variables"""
    if OPENAI_API_KEY:
        print("🔧 Using OpenAI LLM for content generation")
        openai_llm = OpenAILLM(api_key=OPENAI_API_KEY)
        service_factory.set_llm_service(openai_llm)
    else:
        print("🔧 Using Dummy LLM for content generation (set OPENAI_API_KEY to use OpenAI)")

# Configure LLM service
configure_llm_service()
llm_service = service_factory.get_llm_service()
slide_generator = SlideGenerator(cache_service, llm_service)

# Add middleware to the application
app.middleware("http")(rate_limiter)
app.middleware("http")(auth_middleware)
app.middleware("http")(concurrency_controller)

# Include API routers
app.include_router(system_router)
app.include_router(presentation_router, prefix="/api/v1/presentations")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await create_db_and_tables()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 