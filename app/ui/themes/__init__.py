"""
Theme package for PROGAIN PyQt6 application.

This package contains all available themes and theme management utilities.
"""

# Export theme manager functions
from .theme_manager import (
    apply_theme,
    list_themes,
    get_current_theme,
    apply_theme_from_settings
)

# Export theme utilities
from .theme_utils import (
    get_theme_colors,
    adjust_color,
    get_status_color,
    is_dark_theme
)

# Export all themes
from . import charcoal_theme
from . import graphite_theme
from . import slate_theme
from . import dim_theme
from . import amethyst_dim_theme
from . import oceanic_dim_theme
from . import light_theme
from . import fresh_light_theme
from . import professional_light_theme
from . import warm_light_theme

__all__ = [
    # Theme manager
    'apply_theme',
    'list_themes',
    'get_current_theme',
    'apply_theme_from_settings',
    # Theme utilities
    'get_theme_colors',
    'adjust_color',
    'get_status_color',
    'is_dark_theme',
    # Themes
    'charcoal_theme',
    'graphite_theme',
    'slate_theme',
    'dim_theme',
    'amethyst_dim_theme',
    'oceanic_dim_theme',
    'light_theme',
    'fresh_light_theme',
    'professional_light_theme',
    'warm_light_theme',
]
