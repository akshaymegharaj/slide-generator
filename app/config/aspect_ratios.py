"""
Aspect Ratio Configuration
Defines different presentation aspect ratios and their properties
"""
from typing import Dict, Any, Tuple
from enum import Enum
from pptx.util import Inches

class AspectRatio(str, Enum):
    """Available aspect ratios"""
    WIDESCREEN_16_9 = "16:9"      # Standard widescreen
    STANDARD_4_3 = "4:3"          # Traditional standard
    A4_PORTRAIT = "A4"            # A4 paper ratio
    A4_LANDSCAPE = "A4_L"         # A4 landscape
    SQUARE = "1:1"                # Square format
    CUSTOM = "custom"             # Custom dimensions

class AspectRatioConfig:
    """Configuration for different aspect ratios"""
    
    # Aspect ratio definitions with dimensions in inches
    ASPECT_RATIOS = {
        AspectRatio.WIDESCREEN_16_9: {
            "name": "Widescreen (16:9)",
            "description": "Standard widescreen format, great for modern displays",
            "width": 13.33,
            "height": 7.5,
            "width_inches": Inches(13.33),
            "height_inches": Inches(7.5),
            "orientation": "landscape",
            "common_use": "Modern presentations, video displays"
        },
        AspectRatio.STANDARD_4_3: {
            "name": "Standard (4:3)",
            "description": "Traditional standard format, good for older projectors",
            "width": 10,
            "height": 7.5,
            "width_inches": Inches(10),
            "height_inches": Inches(7.5),
            "orientation": "landscape",
            "common_use": "Traditional presentations, older projectors"
        },
        AspectRatio.A4_PORTRAIT: {
            "name": "A4 Portrait",
            "description": "A4 paper ratio in portrait orientation",
            "width": 8.27,
            "height": 11.69,
            "width_inches": Inches(8.27),
            "height_inches": Inches(11.69),
            "orientation": "portrait",
            "common_use": "Print-friendly presentations, documents"
        },
        AspectRatio.A4_LANDSCAPE: {
            "name": "A4 Landscape",
            "description": "A4 paper ratio in landscape orientation",
            "width": 11.69,
            "height": 8.27,
            "width_inches": Inches(11.69),
            "height_inches": Inches(8.27),
            "orientation": "landscape",
            "common_use": "Print-friendly landscape presentations"
        },
        AspectRatio.SQUARE: {
            "name": "Square (1:1)",
            "description": "Square format, great for social media and mobile",
            "width": 10,
            "height": 10,
            "width_inches": Inches(10),
            "height_inches": Inches(10),
            "orientation": "square",
            "common_use": "Social media, mobile presentations"
        }
    }
    
    @classmethod
    def get_aspect_ratio_config(cls, aspect_ratio: AspectRatio) -> Dict[str, Any]:
        """Get configuration for a specific aspect ratio"""
        return cls.ASPECT_RATIOS.get(aspect_ratio, cls.ASPECT_RATIOS[AspectRatio.WIDESCREEN_16_9])
    
    @classmethod
    def get_dimensions(cls, aspect_ratio: AspectRatio) -> Tuple[float, float]:
        """Get width and height in inches for an aspect ratio"""
        config = cls.get_aspect_ratio_config(aspect_ratio)
        return config["width"], config["height"]
    
    @classmethod
    def get_inches_dimensions(cls, aspect_ratio: AspectRatio) -> Tuple[Inches, Inches]:
        """Get width and height as Inches objects for an aspect ratio"""
        config = cls.get_aspect_ratio_config(aspect_ratio)
        return config["width_inches"], config["height_inches"]
    
    @classmethod
    def get_orientation(cls, aspect_ratio: AspectRatio) -> str:
        """Get orientation for an aspect ratio"""
        config = cls.get_aspect_ratio_config(aspect_ratio)
        return config["orientation"]
    
    @classmethod
    def get_name(cls, aspect_ratio: AspectRatio) -> str:
        """Get display name for an aspect ratio"""
        config = cls.get_aspect_ratio_config(aspect_ratio)
        return config["name"]
    
    @classmethod
    def get_description(cls, aspect_ratio: AspectRatio) -> str:
        """Get description for an aspect ratio"""
        config = cls.get_aspect_ratio_config(aspect_ratio)
        return config["description"]
    
    @classmethod
    def get_common_use(cls, aspect_ratio: AspectRatio) -> str:
        """Get common use case for an aspect ratio"""
        config = cls.get_aspect_ratio_config(aspect_ratio)
        return config["common_use"]
    
    @classmethod
    def get_all_aspect_ratios(cls) -> Dict[AspectRatio, Dict[str, Any]]:
        """Get all aspect ratio configurations"""
        return cls.ASPECT_RATIOS.copy()
    
    @classmethod
    def get_available_aspect_ratios(cls) -> list:
        """Get list of available aspect ratio names"""
        return [ratio.value for ratio in AspectRatio if ratio != AspectRatio.CUSTOM]
    
    @classmethod
    def validate_custom_dimensions(cls, width: float, height: float) -> bool:
        """Validate custom dimensions"""
        # Minimum and maximum reasonable dimensions
        min_dimension = 5.0  # 5 inches
        max_dimension = 20.0  # 20 inches
        
        return (min_dimension <= width <= max_dimension and 
                min_dimension <= height <= max_dimension)
    
    @classmethod
    def get_custom_config(cls, width: float, height: float) -> Dict[str, Any]:
        """Get configuration for custom dimensions"""
        if not cls.validate_custom_dimensions(width, height):
            raise ValueError(f"Invalid dimensions: {width}x{height}. Must be between 5 and 20 inches.")
        
        # Determine orientation
        if width > height:
            orientation = "landscape"
        elif height > width:
            orientation = "portrait"
        else:
            orientation = "square"
        
        return {
            "name": f"Custom ({width}\" x {height}\")",
            "description": f"Custom dimensions: {width}\" x {height}\"",
            "width": width,
            "height": height,
            "width_inches": Inches(width),
            "height_inches": Inches(height),
            "orientation": orientation,
            "common_use": "Custom requirements"
        } 