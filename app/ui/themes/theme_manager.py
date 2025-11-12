"""
Theme Manager for PROGAIN PyQt6 application.

Handles theme discovery, loading, and application to the Qt application.
"""

import importlib
import logging
from typing import List, Dict, Optional
from PyQt6.QtWidgets import QApplication

logger = logging.getLogger(__name__)

# Possible packages containing themes
POSSIBLE_THEME_PACKAGES = ['app.ui.themes']

_current_theme = None


def discover_themes() -> List[Dict[str, str]]:
    """
    Discover all available themes by scanning theme packages.
    
    Returns:
        List of theme dictionaries with 'id', 'name', 'description', 'type'
    """
    themes = []
    
    for package_name in POSSIBLE_THEME_PACKAGES:
        try:
            package = importlib.import_module(package_name)
            package_dir = package.__path__[0] if hasattr(package, '__path__') else None
            
            if not package_dir:
                continue
            
            import os
            for filename in os.listdir(package_dir):
                if filename.endswith('_theme.py') and not filename.startswith('__'):
                    theme_id = filename[:-3]  # Remove .py
                    
                    try:
                        module = importlib.import_module(f'{package_name}.{theme_id}')
                        
                        if hasattr(module, 'THEME_METADATA') and hasattr(module, 'THEME_STYLESHEET'):
                            metadata = module.THEME_METADATA
                            themes.append({
                                'id': theme_id,
                                'name': metadata.get('name', theme_id),
                                'description': metadata.get('description', ''),
                                'type': metadata.get('type', 'unknown'),
                                'module': f'{package_name}.{theme_id}'
                            })
                    except Exception as e:
                        logger.warning(f"Failed to load theme {theme_id}: {e}")
                        
        except Exception as e:
            logger.warning(f"Failed to scan package {package_name}: {e}")
    
    return sorted(themes, key=lambda x: x['name'])


def list_themes() -> List[Dict[str, str]]:
    """
    Get list of all available themes.
    
    Returns:
        List of theme dictionaries
    """
    return discover_themes()


def apply_theme(app: QApplication, theme_id: str) -> bool:
    """
    Apply a theme to the application.
    
    Args:
        app: QApplication instance
        theme_id: Theme identifier (e.g., 'charcoal_theme')
    
    Returns:
        True if theme was applied successfully, False otherwise
    """
    global _current_theme
    
    try:
        # Try to import the theme module
        for package_name in POSSIBLE_THEME_PACKAGES:
            try:
                module = importlib.import_module(f'{package_name}.{theme_id}')
                
                if hasattr(module, 'THEME_STYLESHEET'):
                    stylesheet = module.THEME_STYLESHEET
                    app.setStyleSheet(stylesheet)
                    _current_theme = theme_id
                    logger.info(f"Applied theme: {theme_id}")
                    return True
                    
            except ImportError:
                continue
        
        logger.warning(f"Theme not found: {theme_id}")
        return False
        
    except Exception as e:
        logger.error(f"Failed to apply theme {theme_id}: {e}")
        return False


def get_current_theme() -> Optional[str]:
    """
    Get the currently active theme ID.
    
    Returns:
        Theme ID or None if no theme is set
    """
    return _current_theme


def apply_theme_from_settings(app: QApplication) -> bool:
    """
    Apply theme from app settings.
    
    Args:
        app: QApplication instance
    
    Returns:
        True if theme was applied, False otherwise
    """
    try:
        from app.app_settings import get_app_settings
        
        settings = get_app_settings()
        theme_id = settings.get_value('theme', 'charcoal_theme')
        
        return apply_theme(app, theme_id)
        
    except Exception as e:
        logger.error(f"Failed to apply theme from settings: {e}")
        # Apply default theme
        return apply_theme(app, 'charcoal_theme')
