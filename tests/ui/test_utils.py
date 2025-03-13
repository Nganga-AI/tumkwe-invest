"""Test cases for the utils module."""

import unittest
import re
from datetime import datetime, date
from tumkwe_invest.ui.utils import (
    format_currency, format_number, format_percent, format_date, format_timeframe,
    truncate_text, sanitize_html, generate_color_palette, get_trend_color,
    get_contrast_text_color, simplify_large_number, create_theme_config,
    convert_to_frontend_format, AccessibilityUtils
)


class TestFormattingFunctions(unittest.TestCase):
    """Test the formatting utility functions."""

    def test_format_currency(self):
        """Test formatting currency values."""
        # Test with various inputs
        self.assertEqual(format_currency(1234.56), "$1,234.56")
        self.assertEqual(format_currency(1000000), "$1,000,000.00")
        self.assertEqual(format_currency(0), "$0.00")
        self.assertEqual(format_currency(-1234.56), "$-1,234.56")
        
        # Test with different currency symbol
        self.assertEqual(format_currency(1234.56, "€"), "€1,234.56")
        self.assertEqual(format_currency(1234.56, "¥"), "¥1,234.56")

    def test_format_number(self):
        """Test formatting numeric values."""
        # Test with various inputs
        self.assertEqual(format_number(1234.56), "1,234.56")
        self.assertEqual(format_number(1000000), "1,000,000.00")
        self.assertEqual(format_number(0), "0.00")
        self.assertEqual(format_number(-1234.56), "-1,234.56")
        
        # Test with different precision
        self.assertEqual(format_number(1234.56789, 3), "1,234.568")
        self.assertEqual(format_number(1234, 0), "1,234")

    def test_format_percent(self):
        """Test formatting percentage values."""
        # Test with various inputs
        self.assertEqual(format_percent(0.1234), "12.34%")
        self.assertEqual(format_percent(0), "0.00%")
        self.assertEqual(format_percent(-0.1234), "-12.34%")
        
        # Test with different precision
        self.assertEqual(format_percent(0.1234, 1), "12.3%")
        self.assertEqual(format_percent(0.1234, 0), "12%")
        
        # Test with include_sign
        self.assertEqual(format_percent(0.1234, include_sign=True), "+12.34%")
        self.assertEqual(format_percent(-0.1234, include_sign=True), "-12.34%")
        self.assertEqual(format_percent(0, include_sign=True), "0.00%")

    def test_format_date(self):
        """Test formatting date values."""
        # Test with datetime
        dt = datetime(2023, 1, 15, 12, 30, 45)
        self.assertEqual(format_date(dt), "2023-01-15")
        self.assertEqual(format_date(dt, "%m/%d/%Y"), "01/15/2023")
        self.assertEqual(format_date(dt, "%b %d, %Y"), "Jan 15, 2023")
        
        # Test with date
        d = date(2023, 1, 15)
        self.assertEqual(format_date(d), "2023-01-15")
        
        # Test with string
        self.assertEqual(format_date("2023-01-15T12:30:45"), "2023-01-15")
        self.assertEqual(format_date("invalid date"), "invalid date")  # Should return as-is if invalid

    def test_format_timeframe(self):
        """Test formatting timeframe codes."""
        self.assertEqual(format_timeframe("1d"), "Daily")
        self.assertEqual(format_timeframe("1w"), "Weekly")
        self.assertEqual(format_timeframe("1m"), "Monthly")
        self.assertEqual(format_timeframe("3m"), "Quarterly")
        self.assertEqual(format_timeframe("1y"), "Yearly")
        self.assertEqual(format_timeframe("5y"), "5 Years")
        self.assertEqual(format_timeframe("max"), "Maximum")
        self.assertEqual(format_timeframe("unknown"), "unknown")  # Unknown code should return as-is

    def test_truncate_text(self):
        """Test truncating text."""
        # Test with short text (no truncation)
        short_text = "This is short text"
        self.assertEqual(truncate_text(short_text), short_text)
        
        # Test with long text
        long_text = "This is a very long text that should be truncated because it exceeds the maximum length allowed for this function"
        truncated = truncate_text(long_text, max_length=50)
        self.assertEqual(len(truncated), 50)
        self.assertTrue(truncated.endswith("..."))
        self.assertEqual(truncated, long_text[:47] + "...")

    def test_sanitize_html(self):
        """Test sanitizing HTML."""
        # Test removing script tags
        html = "<div>Hello <script>alert('bad')</script> world</div>"
        sanitized = sanitize_html(html)
        self.assertNotIn("<script>", sanitized)
        self.assertIn("<div>Hello  world</div>", sanitized)
        
        # Test removing on* attributes
        html = '<button onclick="bad()">Click</button>'
        sanitized = sanitize_html(html)
        self.assertNotIn("onclick", sanitized)
        self.assertIn("<button>Click</button>", sanitized)
        
        # Test with single quotes
        html = "<div onmouseover='bad()'>Hover</div>"
        sanitized = sanitize_html(html)
        self.assertNotIn("onmouseover", sanitized)
        self.assertIn("<div>Hover</div>", sanitized)


class TestColorFunctions(unittest.TestCase):
    """Test the color utility functions."""

    def test_generate_color_palette(self):
        """Test generating a color palette."""
        # Test generating palette from blue
        blue = "#0000FF"
        palette = generate_color_palette(blue, num_colors=3)
        
        # Should have correct number of colors
        self.assertEqual(len(palette), 3)
        
        # Each color should be a valid hex code
        for color in palette:
            self.assertTrue(re.match(r'^#[0-9a-fA-F]{6}$', color))
        
        # First color should match input color (case-insensitive)
        self.assertEqual(palette[0].lower(), blue.lower())
        
        # Test with single color
        single_palette = generate_color_palette(blue, num_colors=1)
        self.assertEqual(len(single_palette), 1)
        self.assertEqual(single_palette[0].lower(), blue.lower())

    def test_get_trend_color(self):
        """Test getting color based on trend value."""
        # Test positive trend
        positive_color = get_trend_color(0.2)
        self.assertEqual(positive_color, "#34A853")  # Green in light mode
        
        # Test negative trend
        negative_color = get_trend_color(-0.2)
        self.assertEqual(negative_color, "#EA4335")  # Red in light mode
        
        # Test neutral trend (within threshold)
        neutral_color = get_trend_color(0.03)
        self.assertEqual(neutral_color, "#6C757D")  # Gray in light mode
        
        # Test with dark theme
        dark_positive = get_trend_color(0.2, theme="dark")
        self.assertEqual(dark_positive, "#00C853")  # Green in dark mode

    def test_get_contrast_text_color(self):
        """Test getting contrast text color based on background."""
        # Test with dark background
        dark_bg = "#000000"
        self.assertEqual(get_contrast_text_color(dark_bg), "#FFFFFF")  # White text on dark
        
        # Test with light background
        light_bg = "#FFFFFF"
        self.assertEqual(get_contrast_text_color(light_bg), "#000000")  # Black text on light
        
        # Test with medium background
        medium_bg = "#7F7F7F"
        self.assertEqual(get_contrast_text_color(medium_bg), "#FFFFFF")  # White text on medium
        
        # Test with blue background
        blue_bg = "#0000FF"
        self.assertEqual(get_contrast_text_color(blue_bg), "#FFFFFF")  # White text on blue


class TestNumberFormatting(unittest.TestCase):
    """Test number formatting functions."""

    def test_simplify_large_number(self):
        """Test simplifying large numbers."""
        # Test with various inputs
        self.assertEqual(simplify_large_number(123), "123")
        self.assertEqual(simplify_large_number(1234), "1.2K")
        self.assertEqual(simplify_large_number(12345), "12.3K")
        self.assertEqual(simplify_large_number(123456), "123.5K")
        self.assertEqual(simplify_large_number(1234567), "1.2M")
        self.assertEqual(simplify_large_number(1234567890), "1.2B")
        self.assertEqual(simplify_large_number(1234567890000), "1.2T")
        
        # Test with negative numbers
        self.assertEqual(simplify_large_number(-1234), "-1.2K")
        self.assertEqual(simplify_large_number(-1234567), "-1.2M")
        
        # Test with decimals
        self.assertEqual(simplify_large_number(1234.56), "1.2K")


class TestThemeConfig(unittest.TestCase):
    """Test theme configuration functions."""

    def test_create_theme_config(self):
        """Test creating theme configuration."""
        # Test light theme
        light_theme = create_theme_config("Light Theme", is_dark=False, primary_color="#4285F4")
        
        self.assertEqual(light_theme["name"], "Light Theme")
        self.assertFalse(light_theme["dark"])
        self.assertEqual(light_theme["colors"]["primary"], "#4285F4")
        self.assertEqual(light_theme["colors"]["background"], "#FFFFFF")
        self.assertEqual(light_theme["colors"]["text"], "#202124")
        
        # Test dark theme
        dark_theme = create_theme_config("Dark Theme", is_dark=True, primary_color="#4285F4")
        
        self.assertEqual(dark_theme["name"], "Dark Theme")
        self.assertTrue(dark_theme["dark"])
        self.assertEqual(dark_theme["colors"]["primary"], "#4285F4")
        self.assertEqual(dark_theme["colors"]["background"], "#121212")
        self.assertEqual(dark_theme["colors"]["text"], "#FFFFFF")
        
        # Check color palette
        self.assertEqual(len(light_theme["colors"]["palette"]), 5)
        self.assertEqual(len(dark_theme["colors"]["palette"]), 5)


class TestDataConversion(unittest.TestCase):
    """Test data conversion functions."""

    def test_convert_to_frontend_format(self):
        """Test converting data to frontend format."""
        # Test with complex structure
        test_date = datetime(2023, 1, 15)
        data = {
            "string": "value",
            "number": 123,
            "date": test_date,
            "nested": {
                "array": [1, 2, 3],
                "object": {"key": "value"},
                "nested_date": date(2023, 1, 15)
            },
            "list_of_dates": [test_date, date(2023, 2, 15)]
        }
        
        converted = convert_to_frontend_format(data)
        
        # Check string and number remain unchanged
        self.assertEqual(converted["string"], "value")
        self.assertEqual(converted["number"], 123)
        
        # Check dates are converted to ISO format
        self.assertEqual(converted["date"], "2023-01-15T00:00:00")
        self.assertEqual(converted["nested"]["nested_date"], "2023-01-15")
        
        # Check lists and nested objects are preserved
        self.assertEqual(len(converted["nested"]["array"]), 3)
        self.assertEqual(converted["nested"]["object"]["key"], "value")
        
        # Check list of dates
        self.assertEqual(converted["list_of_dates"][0], "2023-01-15T00:00:00")
        self.assertEqual(converted["list_of_dates"][1], "2023-02-15")


class TestAccessibilityUtils(unittest.TestCase):
    """Test accessibility utility functions."""

    def test_get_aria_labels(self):
        """Test generating ARIA labels for components."""
        aria = AccessibilityUtils.get_aria_labels("chart", {"title": "Stock Price"})
        self.assertEqual(aria["aria-label"], "Chart: Stock Price")
        self.assertEqual(aria["role"], "img")
        
        aria = AccessibilityUtils.get_aria_labels("metric", {"title": "P/E Ratio", "value": "15.2"})
        self.assertEqual(aria["aria-label"], "P/E Ratio: 15.2")
        
        aria = AccessibilityUtils.get_aria_labels("button", {"disabled": True})
        self.assertEqual(aria["role"], "button")
        self.assertEqual(aria["aria-disabled"], "true")
        
        aria = AccessibilityUtils.get_aria_labels("toggle", {"checked": True})
        self.assertEqual(aria["role"], "switch")
        self.assertEqual(aria["aria-checked"], "true")

    def test_generate_skip_links(self):
        """Test generating skip navigation links."""
        links = AccessibilityUtils.generate_skip_links()
        
        self.assertEqual(len(links), 2)  # Should have 2 links
        
        # Check main content link
        self.assertEqual(links[0]["id"], "skip-to-main")
        self.assertEqual(links[0]["target"], "main-content")
        self.assertEqual(links[0]["text"], "Skip to main content")
        
        # Check navigation link
        self.assertEqual(links[1]["id"], "skip-to-nav")
        self.assertEqual(links[1]["target"], "main-navigation")
        self.assertEqual(links[1]["text"], "Skip to navigation")

    def test_get_keyboard_shortcuts(self):
        """Test getting keyboard shortcuts."""
        shortcuts = AccessibilityUtils.get_keyboard_shortcuts()
        
        self.assertIn("?", shortcuts)
        self.assertIn("g h", shortcuts)
        self.assertIn("v", shortcuts)
        self.assertEqual(shortcuts["v"], "Toggle view mode")
        self.assertEqual(shortcuts["Esc"], "Close dialogs")


if __name__ == "__main__":
    unittest.main()
