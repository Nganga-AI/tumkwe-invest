"""
UI utility functions for Tumkwe Invest.

This module provides helper functions for UI components, data formatting,
accessibility features, and theme management.
"""

import re
import json
import locale
from typing import Dict, List, Any, Union, Optional
from datetime import datetime, date


def format_currency(value: Union[float, int], currency: str = "$") -> str:
    """
    Format a numeric value as currency.
    
    Args:
        value: Numeric value to format
        currency: Currency symbol
        
    Returns:
        Formatted currency string
    """
    try:
        locale.setlocale(locale.LC_ALL, '')
        formatted = locale.currency(value, grouping=True, symbol=False)
        return f"{currency}{formatted}"
    except (locale.Error, ValueError):
        # Fallback if locale settings fail
        return f"{currency}{value:,.2f}"


def format_number(value: Union[float, int], precision: int = 2) -> str:
    """
    Format a numeric value with thousands separators.
    
    Args:
        value: Numeric value to format
        precision: Number of decimal places
        
    Returns:
        Formatted number string
    """
    try:
        locale.setlocale(locale.LC_ALL, '')
        return locale.format_string(f"%.{precision}f", value, grouping=True)
    except (locale.Error, ValueError):
        # Fallback if locale settings fail
        return f"{value:,.{precision}f}"


def format_percent(value: Union[float, int], precision: int = 2, 
                  include_sign: bool = False) -> str:
    """
    Format a numeric value as a percentage.
    
    Args:
        value: Numeric value to format (0.1 = 10%)
        precision: Number of decimal places
        include_sign: Whether to include + for positive values
        
    Returns:
        Formatted percentage string
    """
    formatted = f"{value * 100:.{precision}f}%"
    if include_sign and value > 0:
        formatted = f"+{formatted}"
    return formatted


def format_date(dt: Union[datetime, date, str], format_str: str = "%Y-%m-%d") -> str:
    """
    Format a date/datetime object as string.
    
    Args:
        dt: Date to format (datetime, date, or string)
        format_str: Format string
        
    Returns:
        Formatted date string
    """
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except ValueError:
            return dt
    
    if isinstance(dt, (datetime, date)):
        return dt.strftime(format_str)
    
    return str(dt)


def format_timeframe(timeframe: str) -> str:
    """
    Format a timeframe code into a human-readable string.
    
    Args:
        timeframe: Timeframe code ('1d', '1w', '1m', etc.)
        
    Returns:
        Human-readable timeframe
    """
    timeframe_map = {
        '1d': 'Daily',
        '1w': 'Weekly',
        '1m': 'Monthly',
        '3m': 'Quarterly',
        '1y': 'Yearly',
        '5y': '5 Years',
        'max': 'Maximum'
    }
    
    return timeframe_map.get(timeframe, timeframe)


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."


def sanitize_html(html: str) -> str:
    """
    Sanitize HTML to prevent XSS attacks.
    
    Args:
        html: HTML string to sanitize
        
    Returns:
        Sanitized HTML
    """
    # Remove script tags and on* attributes
    cleaned = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL)
    cleaned = re.sub(r'\son\w+=".*?"', '', cleaned)
    cleaned = re.sub(r"\son\w+='.*?'", '', cleaned)
    cleaned = re.sub(r'\son\w+=.*?>', '>', cleaned)
    
    return cleaned


def generate_color_palette(base_color: str, num_colors: int = 5) -> List[str]:
    """
    Generate a color palette based on a base color.
    
    Args:
        base_color: Base color in hex format (#RRGGBB)
        num_colors: Number of colors to generate
        
    Returns:
        List of hex color codes
    """
    base_color = base_color.lstrip('#')
    
    # Convert to RGB
    r = int(base_color[0:2], 16)
    g = int(base_color[2:4], 16)
    b = int(base_color[4:6], 16)
    
    # Generate palette
    palette = []
    step = 1.0 / (num_colors - 1) if num_colors > 1 else 1
    
    for i in range(num_colors):
        factor = i * step
        
        # Lighten or darken based on factor
        new_r = min(255, int(r + (255 - r) * factor))
        new_g = min(255, int(g + (255 - g) * factor))
        new_b = min(255, int(b + (255 - b) * factor))
        
        hex_color = f"#{new_r:02x}{new_g:02x}{new_b:02x}"
        palette.append(hex_color)
    
    return palette


def get_trend_color(value: float, neutral_threshold: float = 0.05, 
                   theme: str = "light") -> str:
    """
    Get appropriate color based on trend direction.
    
    Args:
        value: Trend value
        neutral_threshold: Threshold for considering a value neutral
        theme: UI theme ('light' or 'dark')
        
    Returns:
        Hex color code
    """
    colors = {
        "light": {
            "positive": "#34A853",  # Green
            "negative": "#EA4335",  # Red
            "neutral": "#6C757D"    # Gray
        },
        "dark": {
            "positive": "#00C853",
            "negative": "#FF5252",
            "neutral": "#9AA0A6"
        }
    }
    
    theme_colors = colors.get(theme, colors["light"])
    
    if abs(value) < neutral_threshold:
        return theme_colors["neutral"]
    elif value > 0:
        return theme_colors["positive"]
    else:
        return theme_colors["negative"]


def get_contrast_text_color(background_color: str) -> str:
    """
    Get appropriate text color based on background color for accessibility.
    
    Args:
        background_color: Background color in hex format (#RRGGBB)
        
    Returns:
        Text color ('#FFFFFF' or '#000000')
    """
    background_color = background_color.lstrip('#')
    
    # Convert to RGB
    r = int(background_color[0:2], 16)
    g = int(background_color[2:4], 16)
    b = int(background_color[4:6], 16)
    
    # Calculate perceived brightness (YIQ formula)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    
    # Return white for dark backgrounds, black for light backgrounds
    return '#FFFFFF' if brightness < 128 else '#000000'


def simplify_large_number(value: Union[int, float]) -> str:
    """
    Convert large numbers to simplified format (K, M, B).
    
    Args:
        value: Number to simplify
        
    Returns:
        Simplified string representation
    """
    if abs(value) < 1000:
        return str(value)
    
    for suffix in ['', 'K', 'M', 'B', 'T']:
        if abs(value) < 1000:
            return f"{value:.1f}{suffix}".replace('.0', '')
        value /= 1000
    
    return f"{value:.1f}T"


def create_theme_config(theme_name: str, is_dark: bool = False, 
                       primary_color: str = "#4285F4") -> Dict[str, Any]:
    """
    Create a theme configuration object.
    
    Args:
        theme_name: Name of the theme
        is_dark: Whether it's a dark theme
        primary_color: Primary color in hex format
        
    Returns:
        Theme configuration dictionary
    """
    text_color = "#FFFFFF" if is_dark else "#202124"
    background_color = "#121212" if is_dark else "#FFFFFF"
    
    # Generate a palette based on primary color
    palette = generate_color_palette(primary_color, 5)
    
    theme = {
        "name": theme_name,
        "dark": is_dark,
        "colors": {
            "primary": primary_color,
            "secondary": palette[2],
            "accent": palette[4],
            "background": background_color,
            "text": text_color,
            "border": "#E0E0E0" if not is_dark else "#333333",
            "positive": "#34A853" if not is_dark else "#00C853",
            "negative": "#EA4335" if not is_dark else "#FF5252",
            "neutral": "#4285F4" if not is_dark else "#448AFF",
            "palette": palette
        }
    }
    
    return theme


def convert_to_frontend_format(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert backend data format to frontend-friendly format.
    
    Args:
        data: Backend data object
        
    Returns:
        Frontend-friendly data format
    """
    # Default transformation for common data structures
    if isinstance(data, dict):
        return {k: convert_to_frontend_format(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_to_frontend_format(item) for item in data]
    elif isinstance(data, (datetime, date)):
        return data.isoformat()
    else:
        return data


class AccessibilityUtils:
    """Utility class for accessibility features."""
    
    @staticmethod
    def get_aria_labels(component_type: str, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate ARIA labels for a component.
        
        Args:
            component_type: Type of component
            data: Component data
            
        Returns:
            Dictionary of ARIA attributes
        """
        aria = {}
        
        if component_type == "chart":
            aria["aria-label"] = f"Chart: {data.get('title', 'Data visualization')}"
            aria["role"] = "img"
            
        elif component_type == "metric":
            value = data.get("value", "")
            title = data.get("title", "")
            aria["aria-label"] = f"{title}: {value}"
            
        elif component_type == "button":
            aria["role"] = "button"
            if data.get("disabled"):
                aria["aria-disabled"] = "true"
                
        elif component_type == "toggle":
            aria["role"] = "switch"
            aria["aria-checked"] = "true" if data.get("checked") else "false"
            
        return aria
    
    @staticmethod
    def generate_skip_links() -> List[Dict[str, str]]:
        """
        Generate skip navigation links for accessibility.
        
        Returns:
            List of skip link configurations
        """
        return [
            {
                "id": "skip-to-main",
                "target": "main-content",
                "text": "Skip to main content"
            },
            {
                "id": "skip-to-nav",
                "target": "main-navigation",
                "text": "Skip to navigation"
            }
        ]
        
    @staticmethod
    def get_keyboard_shortcuts() -> Dict[str, str]:
        """
        Get keyboard shortcuts for the UI.
        
        Returns:
            Dictionary mapping key combinations to actions
        """
        return {
            "?": "Show keyboard shortcuts",
            "g h": "Go to home",
            "g d": "Go to dashboard",
            "g a": "Go to analysis",
            "t": "Toggle theme",
            "v": "Toggle view mode",
            "Esc": "Close dialogs"
        }
