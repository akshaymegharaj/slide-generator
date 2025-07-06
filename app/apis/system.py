"""
System API routes for health check, cache management, LLM service, and concurrency
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from app.services.factory import service_factory
from app.services.impl.openai_llm import OpenAILLM
from app.middleware import concurrency_controller

router = APIRouter()

# Initialize services
cache_service = service_factory.get_cache_service()

@router.get("/", tags=["Admin"])
async def root():
    """Health check endpoint"""
    return {"message": "Slide Generator API is running"}

@router.get("/api/v1/cache/stats", tags=["Admin"])
async def get_cache_stats():
    """Get cache statistics"""
    return cache_service.get_cache_stats()

@router.post("/api/v1/cache/clear", tags=["Admin"])
async def clear_cache():
    """Clear all caches"""
    cache_service.clear_all()
    return {"message": "All caches cleared"}

@router.get("/api/v1/llm/status", tags=["Admin"])
async def get_llm_status():
    """Get current LLM service status"""
    current_llm = service_factory.get_llm_service()
    return {
        "llm_service": type(current_llm).__name__,
        "is_openai": isinstance(current_llm, OpenAILLM),
        "is_dummy": "DummyLLM" in type(current_llm).__name__
    }

@router.get("/api/v1/concurrency/stats", tags=["Admin"])
async def get_concurrency_stats():
    """Get concurrency statistics"""
    return concurrency_controller.get_concurrency_stats()

@router.post("/api/v1/llm/switch", tags=["Admin"])
async def switch_llm_service(llm_type: str = "dummy", api_key: Optional[str] = None):
    """Switch LLM service implementation"""
    try:
        if llm_type.lower() == "openai":
            if not api_key:
                raise HTTPException(status_code=400, detail="API key required for OpenAI")
            openai_llm = OpenAILLM(api_key=api_key)
            service_factory.set_llm_service(openai_llm)
            return {"message": "Switched to OpenAI LLM", "llm_service": "OpenAILLM"}
        
        elif llm_type.lower() == "dummy":
            from app.services.dummy_llm import DummyLLM
            dummy_llm = DummyLLM()
            service_factory.set_llm_service(dummy_llm)
            return {"message": "Switched to Dummy LLM", "llm_service": "DummyLLM"}
        
        else:
            raise HTTPException(status_code=400, detail="Invalid LLM type. Use 'openai' or 'dummy'")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to switch LLM service: {str(e)}") 