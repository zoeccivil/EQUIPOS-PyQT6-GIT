"""
Theme utilities for PROGAIN PyQt6 application.

Provides helper functions for working with theme colors and styles.
"""

import re
from typing import Dict, Tuple, Optional
from PyQt6.QtGui import QColor


def parse_color(color_str: str) -> Tuple[int, int, int]:
    """
    Parse a color string (#RRGGBB) to RGB tuple.
    
    Args:
        color_str: Color in hex format (#RRGGBB)
    
    Returns:
        Tuple of (r, g, b) values
    """
    color_str = color_str.lstrip('#')
    return tuple(int(color_str[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Convert RGB values to hex color string.
    
    Args:
        r, g, b: RGB color values (0-255)
    
    Returns:
        Hex color string (#RRGGBB)
    """
    return f"#{r:02x}{g:02x}{b:02x}"


def adjust_color(color_str: str, factor: float) -> str:
    """
    Adjust color brightness.
    
    Args:
        color_str: Color in hex format (#RRGGBB)
        factor: Brightness factor (>1 lighter, <1 darker)
    
    Returns:
        Adjusted color in hex format
    """
    r, g, b = parse_color(color_str)
    
    r = int(min(255, r * factor))
    g = int(min(255, g * factor))
    b = int(min(255, b * factor))
    
    return rgb_to_hex(r, g, b)


def get_theme_colors() -> Dict[str, str]:
    """
    Extract colors from the current theme stylesheet.
    
    Returns:
        Dictionary of color names to hex values
    """
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if not app:
        return {}
    
    stylesheet = app.styleSheet()
    colors = {}
    
    # Extract background colors
    bg_match = re.search(r'QMainWindow\s*\{[^}]*background-color:\s*([#\w]+)', stylesheet)
    if bg_match:
        colors['background'] = bg_match.group(1)
    
    # Extract foreground colors
    fg_match = re.search(r'QMainWindow\s*\{[^}]*color:\s*([#\w]+)', stylesheet)
    if fg_match:
        colors['foreground'] = fg_match.group(1)
    
    # Extract accent color from buttons
    accent_match = re.search(r'QPushButton\s*\{[^}]*border:\s*[^;]*\s+([#\w]+)', stylesheet)
    if accent_match:
        colors['accent'] = accent_match.group(1)
    
    return colors


def get_status_color(status: str) -> str:
    """
    Get semantic status color.
    
    Args:
        status: Status type ('success', 'warning', 'error', 'info')
    
    Returns:
        Hex color string
    """
    status_colors = {
        'success': '#4caf50',  # Green
        'warning': '#ff9800',  # Orange
        'error': '#f44336',    # Red
        'info': '#2196f3'      # Blue
    }
    
    return status_colors.get(status, '#666666')


def is_dark_theme() -> bool:
    """
    Detect if current theme is dark based on background color.
    
    Returns:
        True if theme is dark, False otherwise
    """
    colors = get_theme_colors()
    bg = colors.get('background', '#ffffff')
    
    r, g, b = parse_color(bg)
    
    # Calculate luminance
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    
    return luminance < 0.5
