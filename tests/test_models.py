"""
Tests for model components
"""
import pytest
import json
from datetime import datetime
from app.models.presentation import Presentation, Slide, PresentationConfig, SlideType
from app.models.database import PresentationDB
from app.config.themes import ThemeConfig, Theme
from app.config.aspect_ratios import AspectRatioConfig, AspectRatio

class TestSlide:
    """Test Slide model"""
    
    def test_slide_initialization(self):
        """Test slide initialization"""
        slide = Slide(
            slide_type=SlideType.TITLE,
            title="Test Slide",
            content=["Test content"]
        )
        
        assert slide.slide_type == SlideType.TITLE
        assert slide.title == "Test Slide"
        assert slide.content == ["Test content"]
        assert slide.citations == []
    
    def test_slide_with_citations(self):
        """Test slide with citations"""
        citations = ["Test Citation 1", "Test Citation 2"]
        
        slide = Slide(
            slide_type=SlideType.BULLET_POINTS,
            title="Test Slide",
            content=["Point 1", "Point 2"],
            citations=citations
        )
        
        assert len(slide.citations) == 2
        assert slide.citations[0] == "Test Citation 1"
    
    def test_slide_to_dict(self):
        """Test slide to dictionary conversion"""
        slide = Slide(
            slide_type=SlideType.TITLE,
            title="Test Slide",
            content=["Test content"]
        )
        
        slide_dict = slide.dict()
        
        assert slide_dict["slide_type"] == "title"
        assert slide_dict["title"] == "Test Slide"
        assert slide_dict["content"] == ["Test content"]
        assert "citations" in slide_dict

class TestPresentationConfig:
    """Test PresentationConfig model"""
    
    def test_presentation_config_initialization(self):
        """Test presentation config initialization"""
        config = PresentationConfig(
            theme=Theme.MODERN,
            font="Arial",
            colors={
                "primary": "#FF0000",
                "secondary": "#00FF00",
                "background": "#FFFFFF",
                "text": "#000000"
            },
            aspect_ratio=AspectRatio.WIDESCREEN_16_9
        )
        
        assert config.theme == Theme.MODERN
        assert config.font == "Arial"
        assert config.colors["primary"] == "#FF0000"
        assert config.aspect_ratio == AspectRatio.WIDESCREEN_16_9
    
    def test_presentation_config_defaults(self):
        """Test presentation config with defaults"""
        config = PresentationConfig()
        
        assert config.theme == Theme.MODERN
        assert config.font == ThemeConfig.get_theme_font(Theme.MODERN)
        assert config.aspect_ratio == AspectRatio.WIDESCREEN_16_9
    
    def test_presentation_config_custom_aspect_ratio(self):
        """Test presentation config with custom aspect ratio"""
        config = PresentationConfig(
            aspect_ratio=AspectRatio.CUSTOM,
            custom_width=12.0,
            custom_height=8.0
        )
        
        assert config.aspect_ratio == AspectRatio.CUSTOM
        assert config.custom_width == 12.0
        assert config.custom_height == 8.0

class TestPresentation:
    """Test Presentation model"""
    
    def test_presentation_initialization(self):
        """Test presentation initialization"""
        slides = [
            Slide(slide_type=SlideType.TITLE, title="Slide 1", content=["Content 1"]),
            Slide(slide_type=SlideType.BULLET_POINTS, title="Slide 2", content=["Content 2"])
        ]
        
        presentation = Presentation(
            id="presentation-1",
            topic="Test Presentation",
            num_slides=2,
            slides=slides,
            theme=Theme.MODERN,
            aspect_ratio=AspectRatio.WIDESCREEN_16_9
        )
        
        assert presentation.id == "presentation-1"
        assert presentation.topic == "Test Presentation"
        assert presentation.num_slides == 2
        assert len(presentation.slides) == 2
        assert presentation.theme == Theme.MODERN
        assert presentation.aspect_ratio == AspectRatio.WIDESCREEN_16_9
    
    def test_presentation_custom_aspect_ratio(self):
        """Test presentation with custom aspect ratio"""
        presentation = Presentation(
            id="presentation-1",
            topic="Test Presentation",
            num_slides=1,
            slides=[Slide(slide_type=SlideType.TITLE, title="Slide 1", content=["Content 1"])],
            aspect_ratio=AspectRatio.CUSTOM,
            custom_width=12.0,
            custom_height=8.0
        )
        
        assert presentation.aspect_ratio == AspectRatio.CUSTOM
        assert presentation.custom_width == 12.0
        assert presentation.custom_height == 8.0

class TestPresentationDB:
    """Test PresentationDB model"""
    
    def test_presentation_db_initialization(self):
        """Test presentation DB initialization"""
        presentation_db = PresentationDB(
            id="presentation-1",
            topic="Test Presentation",
            num_slides=1,
            theme=Theme.MODERN,
            aspect_ratio=AspectRatio.WIDESCREEN_16_9
        )
        
        assert presentation_db.id == "presentation-1"
        assert presentation_db.topic == "Test Presentation"
        assert presentation_db.num_slides == 1
        assert presentation_db.theme == Theme.MODERN
        assert presentation_db.aspect_ratio == AspectRatio.WIDESCREEN_16_9
    
    def test_presentation_db_custom_aspect_ratio(self):
        """Test presentation DB with custom aspect ratio"""
        presentation_db = PresentationDB(
            id="presentation-1",
            topic="Test Presentation",
            num_slides=1,
            theme=Theme.MODERN,
            aspect_ratio=AspectRatio.CUSTOM,
            custom_width=12.0,
            custom_height=8.0
        )
        
        assert presentation_db.aspect_ratio == AspectRatio.CUSTOM
        assert presentation_db.custom_width == 12.0
        assert presentation_db.custom_height == 8.0

class TestThemeConfig:
    """Test theme configuration"""
    
    def test_get_theme_config_modern(self):
        """Test modern theme configuration"""
        config = ThemeConfig.get_theme_config(Theme.MODERN)
        
        assert config["name"] == "Modern"
        assert "colors" in config
        assert "font" in config
    
    def test_get_theme_config_minimal(self):
        """Test minimal theme configuration"""
        config = ThemeConfig.get_theme_config(Theme.MINIMAL)
        
        assert config["name"] == "Minimal"
        assert config["colors"]["background"] == "#000000"
        assert config["colors"]["text"] == "#FFFFFF"
    
    def test_get_theme_config_classic(self):
        """Test classic theme configuration"""
        config = ThemeConfig.get_theme_config(Theme.CLASSIC)
        
        assert config["name"] == "Classic"
        assert config["colors"]["primary"] == "#1F4E79"
        assert config["colors"]["secondary"] == "#D4AF37"
    
    def test_get_theme_config_corporate(self):
        """Test corporate theme configuration"""
        config = ThemeConfig.get_theme_config(Theme.CORPORATE)
        
        assert config["name"] == "Corporate"
        assert config["colors"]["primary"] == "#3498DB"
        assert config["colors"]["secondary"] == "#2ECC71"
    
    def test_get_theme_config_nonexistent(self):
        """Test getting non-existent theme configuration"""
        # This should return the default theme (modern)
        config = ThemeConfig.get_theme_config(Theme.MODERN)
        assert config["name"] == "Modern"
    
    def test_get_available_themes(self):
        """Test getting available themes"""
        themes = ThemeConfig.get_available_themes()
        
        assert "modern" in themes
        assert "minimal" in themes
        assert "classic" in themes
        assert "corporate" in themes

class TestAspectRatioConfig:
    """Test aspect ratio configuration"""
    
    def test_get_aspect_ratio_config_16_9(self):
        """Test 16:9 aspect ratio configuration"""
        config = AspectRatioConfig.get_aspect_ratio_config(AspectRatio.WIDESCREEN_16_9)
        
        assert config["name"] == "Widescreen (16:9)"
        assert config["width"] == 13.33
        assert config["height"] == 7.5
    
    def test_get_aspect_ratio_config_4_3(self):
        """Test 4:3 aspect ratio configuration"""
        config = AspectRatioConfig.get_aspect_ratio_config(AspectRatio.STANDARD_4_3)
        
        assert config["name"] == "Standard (4:3)"
        assert config["width"] == 10
        assert config["height"] == 7.5
    
    def test_get_aspect_ratio_config_square(self):
        """Test square aspect ratio configuration"""
        config = AspectRatioConfig.get_aspect_ratio_config(AspectRatio.SQUARE)
        
        assert config["name"] == "Square (1:1)"
        assert config["width"] == 10
        assert config["height"] == 10
    
    def test_get_available_aspect_ratios(self):
        """Test getting available aspect ratios"""
        ratios = AspectRatioConfig.get_available_aspect_ratios()
        
        assert "16:9" in ratios
        assert "4:3" in ratios
        assert "A4" in ratios
        assert "A4_L" in ratios
        assert "1:1" in ratios
        assert "custom" not in ratios  # Custom should not be in available list
    
    def test_validate_custom_dimensions_valid(self):
        """Test custom dimension validation with valid dimensions"""
        assert AspectRatioConfig.validate_custom_dimensions(10.0, 7.5) is True
        assert AspectRatioConfig.validate_custom_dimensions(5.0, 5.0) is True
        assert AspectRatioConfig.validate_custom_dimensions(20.0, 20.0) is True
    
    def test_validate_custom_dimensions_invalid(self):
        """Test custom dimension validation with invalid dimensions"""
        assert AspectRatioConfig.validate_custom_dimensions(3.0, 7.5) is False  # Too small
        assert AspectRatioConfig.validate_custom_dimensions(25.0, 7.5) is False  # Too large
        assert AspectRatioConfig.validate_custom_dimensions(10.0, 2.0) is False  # Too small
    
    def test_get_custom_config(self):
        """Test getting custom configuration"""
        config = AspectRatioConfig.get_custom_config(12.0, 8.0)
        
        assert config["name"] == "Custom (12.0\" x 8.0\")"
        assert config["width"] == 12.0
        assert config["height"] == 8.0
        assert config["orientation"] == "landscape"
    
    def test_get_custom_config_invalid(self):
        """Test getting custom configuration with invalid dimensions"""
        with pytest.raises(ValueError):
            AspectRatioConfig.get_custom_config(3.0, 8.0) 