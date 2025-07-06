"""
Configuration API routes for aspect ratios and other config options
"""
from fastapi import APIRouter
from app.config.aspect_ratios import AspectRatioConfig, AspectRatio

router = APIRouter()

@router.get("/api/v1/aspect-ratios")
async def get_aspect_ratios():
    """Get available aspect ratios"""
    aspect_ratios = {}
    for ratio in AspectRatio:
        if ratio != AspectRatio.CUSTOM:
            config = AspectRatioConfig.get_aspect_ratio_config(ratio)
            aspect_ratios[ratio.value] = {
                "name": config["name"],
                "description": config["description"],
                "width": config["width"],
                "height": config["height"],
                "orientation": config["orientation"],
                "common_use": config["common_use"]
            }
    
    return {
        "available_aspect_ratios": aspect_ratios,
        "custom_support": True,
        "custom_limits": {
            "min_width": 5.0,
            "max_width": 20.0,
            "min_height": 5.0,
            "max_height": 20.0
        }
    } 