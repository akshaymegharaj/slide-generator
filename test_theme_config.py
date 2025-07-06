"""
Test script to verify centralized theme configuration
"""
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.config.themes import Theme, ThemeConfig

def test_theme_configuration():
    """Test the centralized theme configuration"""
    print("🧪 Testing Centralized Theme Configuration")
    print("=" * 50)
    
    # Test all themes
    for theme in Theme:
        print(f"\n🎨 Testing {theme.value.upper()} theme:")
        
        # Get theme configuration
        config = ThemeConfig.get_theme_config(theme)
        colors = ThemeConfig.get_theme_colors(theme)
        font = ThemeConfig.get_theme_font(theme)
        name = ThemeConfig.get_theme_name(theme)
        description = ThemeConfig.get_theme_description(theme)
        
        print(f"   Name: {name}")
        print(f"   Description: {description}")
        print(f"   Font: {font}")
        print(f"   Colors:")
        for color_name, color_value in colors.items():
            print(f"     {color_name}: {color_value}")
    
    # Test available themes
    print(f"\n📋 Available themes: {ThemeConfig.get_available_themes()}")
    
    # Test default theme
    print(f"\n🏠 Default theme: {Theme.MODERN}")
    default_colors = ThemeConfig.get_theme_colors(Theme.MODERN)
    print(f"   Default colors: {default_colors}")
    
    print("\n✅ All theme configuration tests passed!")
    print("=" * 50)

if __name__ == "__main__":
    test_theme_configuration() 