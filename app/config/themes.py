from typing import Dict, Any
from enum import Enum

class Theme(str, Enum):
    """Available themes"""
    MODERN = "modern"
    CLASSIC = "classic"
    MINIMAL = "minimal"
    CORPORATE = "corporate"

class ThemeConfig:
    """Centralized theme configuration"""
    
    # Theme definitions with updated distinct color schemes
    THEMES = {
        Theme.MODERN: {
            "name": "Modern",
            "description": "Clean, vibrant design with blue-purple gradient",
            "font": "Segoe UI",
            "colors": {
                "primary": "#2E86AB",      # Ocean blue
                "secondary": "#A23B72",    # Deep purple
                "background": "#FFFFFF",   # Pure white
                "text": "#2C3E50",         # Dark slate
                "accent": "#3498DB"        # Bright blue
            }
        },
        Theme.CLASSIC: {
            "name": "Classic",
            "description": "Traditional business look with navy and gold",
            "font": "Georgia",
            "colors": {
                "primary": "#1F4E79",      # Navy blue
                "secondary": "#D4AF37",    # Gold
                "background": "#F8F9FA",   # Off-white
                "text": "#2C3E50",         # Dark blue-gray
                "accent": "#4682B4"        # Steel blue
            }
        },
        Theme.MINIMAL: {
            "name": "Minimal",
            "description": "Simple, clean design with black background",
            "font": "Arial",
            "colors": {
                "primary": "#E74C3C",      # Red
                "secondary": "#F39C12",    # Orange
                "background": "#000000",   # Pure black
                "text": "#FFFFFF",         # White
                "accent": "#ECF0F1"        # Light gray
            }
        },
        Theme.CORPORATE: {
            "name": "Corporate",
            "description": "Professional business look with dark blue background",
            "font": "Roboto",
            "colors": {
                "primary": "#3498DB",      # Blue
                "secondary": "#2ECC71",    # Green
                "background": "#1A1A2E",   # Dark blue
                "text": "#E8E8E8",         # Light gray
                "accent": "#F39C12"        # Orange
            }
        }
    }
    
    @classmethod
    def get_theme_config(cls, theme: Theme) -> Dict[str, Any]:
        """Get configuration for a specific theme"""
        return cls.THEMES.get(theme, cls.THEMES[Theme.MODERN])
    
    @classmethod
    def get_theme_colors(cls, theme: Theme) -> Dict[str, str]:
        """Get colors for a specific theme"""
        config = cls.get_theme_config(theme)
        return config.get("colors", {})
    
    @classmethod
    def get_theme_font(cls, theme: Theme) -> str:
        """Get font for a specific theme"""
        config = cls.get_theme_config(theme)
        return config.get("font", "Arial")
    
    @classmethod
    def get_theme_name(cls, theme: Theme) -> str:
        """Get display name for a specific theme"""
        config = cls.get_theme_config(theme)
        return config.get("name", "Unknown")
    
    @classmethod
    def get_theme_description(cls, theme: Theme) -> str:
        """Get description for a specific theme"""
        config = cls.get_theme_config(theme)
        return config.get("description", "")
    
    @classmethod
    def get_all_themes(cls) -> Dict[Theme, Dict[str, Any]]:
        """Get all theme configurations"""
        return cls.THEMES.copy()
    
    @classmethod
    def get_available_themes(cls) -> list:
        """Get list of available theme names"""
        return [theme.value for theme in Theme] 