"""
Advanced tests for UI utility functions in Tumkwe Invest.
"""

import re
import unittest
from datetime import date, datetime, timedelta

from tumkwe_invest.ui.utils import (
    AccessibilityUtils,
    convert_to_frontend_format,
    create_theme_config,
    format_currency,
    format_date,
    format_percent,
    generate_color_palette,
    get_contrast_text_color,
    get_trend_color,
    sanitize_html,
    simplify_large_number,
    truncate_text,
)


class TestFormattingEdgeCases(unittest.TestCase):
    def test_format_currency_edge_cases(self):
        # Test zero
        self.assertIn("$0", format_currency(0))

        # Test negative values
        neg_result = format_currency(-1234.56)
        self.assertIn("-", neg_result)
        self.assertIn("$", neg_result)

        # Test very large values
        large_result = format_currency(1234567890.12)
        self.assertIn("$", large_result)
        self.assertIn("1", large_result)
        self.assertIn("234", large_result)
        self.assertIn("567", large_result)
        self.assertIn("890", large_result)

    def test_format_percent_edge_cases(self):
        # Test zero
        self.assertEqual(format_percent(0), "0.00%")

        # Test negative with sign
        self.assertEqual(format_percent(-0.1234, 2, True), "-12.34%")

        # Test very small positive with sign
        self.assertEqual(format_percent(0.00001, 4, True), "+0.0010%")

        # Test very small negative with sign
        self.assertEqual(format_percent(-0.00001, 4, True), "-0.0010%")

    def test_format_date_edge_cases(self):
        # Test with future date
        future = datetime.now() + timedelta(days=365)
        self.assertEqual(format_date(future), future.strftime("%Y-%m-%d"))

        # Test with very old date
        old_date = date(1900, 1, 1)
        self.assertEqual(format_date(old_date), "1900-01-01")

        # Test with non-standard format
        dt = datetime(2023, 4, 15, 10, 30, 0)
        self.assertEqual(format_date(dt, "%B %d, %Y"), "April 15, 2023")

        # Test with timestamp string
        self.assertEqual(format_date("2023-04-15T10:30:00.000Z"), "2023-04-15")

    def test_truncate_text_edge_cases(self):
        # Test empty string
        self.assertEqual(truncate_text(""), "")

        # Test exactly at max length
        self.assertEqual(truncate_text("12345", 5), "12345")

        # Test very short max length
        self.assertEqual(truncate_text("abcdef", 3), "...")

        # Test with only spaces
        self.assertLessEqual(len(truncate_text("          ", 5)), 5)

    def test_sanitize_html_advanced(self):
        # Test nested script tags
        nested = (
            "<div><script>bad()</script><p>Good</p><script>also_bad()</script></div>"
        )
        sanitized = sanitize_html(nested)
        self.assertNotIn("<script>", sanitized)
        self.assertIn("<p>Good</p>", sanitized)

        # Test script with attributes
        script_attr = '<script type="text/javascript" src="evil.js"></script>'
        sanitized = sanitize_html(script_attr)
        self.assertNotIn("script", sanitized)
        self.assertNotIn("evil.js", sanitized)

        # Test event handlers in different formats
        attrs = '<a onclick="evil()" href="#">Link</a><div ONCLICK=\'bad()\'></div>'
        sanitized = sanitize_html(attrs)
        self.assertIn("onclick", sanitized.lower())
        self.assertIn("Link", sanitized)

    def test_simplify_large_number_edge_cases(self):
        # Test zero
        self.assertEqual(simplify_large_number(0), "0")

        # Test negative numbers
        self.assertEqual(simplify_large_number(-1500), "-1.5K")
        self.assertEqual(simplify_large_number(-1000000), "-1M")

        # Test numbers at boundaries
        self.assertEqual(simplify_large_number(999), "999")  # Below 1K
        self.assertEqual(simplify_large_number(1000), "1K")  # Exactly 1K
        self.assertEqual(simplify_large_number(1000000), "1M")  # Exactly 1M

        # Test rounding
        self.assertEqual(simplify_large_number(1499), "1.5K")  # Should round to 1.5K
        self.assertEqual(simplify_large_number(1050), "1.1K")  # Should round to 1.1K


class TestColorFunctions(unittest.TestCase):
    def test_generate_color_palette_edge_cases(self):
        # Test with invalid hex color
        with self.assertRaises(Exception):
            generate_color_palette("not-a-hex-color", 3)

        # Test with short hex color format
        short_hex_result = generate_color_palette("#34A853", 3)
        self.assertEqual(len(short_hex_result), 3)
        for color in short_hex_result:
            self.assertTrue(re.match(r"^#[0-9a-f]{6}$", color))

    def test_get_trend_color_edge_cases(self):
        # Test with zero
        zero_color = get_trend_color(0)
        self.assertEqual(zero_color, "#6C757D")  # Neutral color

        # Test with values just above/below threshold
        just_above = get_trend_color(0.051)  # Just above 0.05 threshold
        just_below = get_trend_color(0.049)  # Just below 0.05 threshold
        self.assertNotEqual(just_above, just_below)

        # Test very large values
        large_positive = get_trend_color(100)
        large_negative = get_trend_color(-100)
        self.assertEqual(large_positive, "#34A853")  # Should be positive color
        self.assertEqual(large_negative, "#EA4335")  # Should be negative color

    def test_get_contrast_text_color_edge_cases(self):
        # Test with grayscale colors at the midpoint
        mid_gray = get_contrast_text_color("#7F7F7F")
        self.assertIn(mid_gray, ["#000000", "#FFFFFF"])

        # Test pure colors
        self.assertEqual(get_contrast_text_color("#FF0000"), "#FFFFFF")  # Pure red
        self.assertEqual(get_contrast_text_color("#00FF00"), "#000000")  # Pure green
        self.assertEqual(get_contrast_text_color("#0000FF"), "#FFFFFF")  # Pure blue

        # Test edge colors
        self.assertEqual(get_contrast_text_color("#000001"), "#FFFFFF")  # Almost black
        self.assertEqual(get_contrast_text_color("#FFFFFE"), "#000000")  # Almost white


class TestConversionFunctions(unittest.TestCase):
    def test_convert_to_frontend_format_complex_structures(self):
        # Create a complex nested structure with dates
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        complex_obj = {
            "dates": {
                "today": today,
                "yesterday": yesterday,
                "string_date": "2023-01-01",
            },
            "metrics": [
                {"date": today, "value": 100},
                {"date": yesterday, "value": 95},
            ],
            "nested": {"deep": {"deeper": {"deepest": today}}},
            "mixed_array": [today, "string", {"date": yesterday}, [today, yesterday]],
        }

        # Convert to frontend format
        converted = convert_to_frontend_format(complex_obj)

        # Verify all dates are converted to ISO format strings
        self.assertEqual(converted["dates"]["today"], today.isoformat())
        self.assertEqual(converted["dates"]["yesterday"], yesterday.isoformat())
        self.assertEqual(converted["dates"]["string_date"], "2023-01-01")  # Unchanged

        self.assertEqual(converted["metrics"][0]["date"], today.isoformat())
        self.assertEqual(converted["metrics"][1]["date"], yesterday.isoformat())

        self.assertEqual(
            converted["nested"]["deep"]["deeper"]["deepest"], today.isoformat()
        )

        self.assertEqual(converted["mixed_array"][0], today.isoformat())
        self.assertEqual(converted["mixed_array"][1], "string")  # Unchanged
        self.assertEqual(converted["mixed_array"][2]["date"], yesterday.isoformat())
        self.assertEqual(converted["mixed_array"][3][0], today.isoformat())
        self.assertEqual(converted["mixed_array"][3][1], yesterday.isoformat())


class TestThemeConfigFunctions(unittest.TestCase):
    def test_create_theme_config_variations(self):
        # Test custom theme name and color
        custom_theme = create_theme_config(
            "Custom Purple Theme", True, "#6200EE"  # Dark mode  # Purple
        )

        self.assertEqual(custom_theme["name"], "Custom Purple Theme")
        self.assertTrue(custom_theme["dark"])
        self.assertEqual(custom_theme["colors"]["primary"], "#6200EE")

        # Test automatic contrast colors
        self.assertEqual(custom_theme["colors"]["text"], "#FFFFFF")  # Dark mode text
        self.assertEqual(
            custom_theme["colors"]["background"], "#121212"
        )  # Dark mode background

        # Test palette generation
        self.assertEqual(len(custom_theme["colors"]["palette"]), 5)
        self.assertEqual(custom_theme["colors"]["palette"][0], "#6200ee")  # Base color

        # Verify other colors are properly set based on theme
        self.assertEqual(
            custom_theme["colors"]["positive"], "#00C853"
        )  # Dark mode positive
        self.assertEqual(
            custom_theme["colors"]["border"], "#333333"
        )  # Dark mode border


class TestAccessibilityUtils(unittest.TestCase):
    def test_get_aria_labels_complex_cases(self):
        utils = AccessibilityUtils()

        # Test compound components
        compound_data = {
            "title": "Performance Metrics",
            "disabled": True,
            "expanded": False,
            "required": True,
            "checked": True,
            "value": "High Value",
        }

        aria = utils.get_aria_labels("button", compound_data)

        # Should include all relevant attributes
        self.assertIn("aria-disabled", aria)
        self.assertEqual(aria["aria-disabled"], "true")

    def test_generate_skip_links_custom(self):
        utils = AccessibilityUtils()

        # Generate default skip links
        default_links = utils.generate_skip_links()

        # Verify structure and essential links
        self.assertGreaterEqual(len(default_links), 2)

        # Check main content link
        main_links = [
            link for link in default_links if link["target"] == "main-content"
        ]
        self.assertEqual(len(main_links), 1)

        # Check navigation link
        nav_links = [
            link for link in default_links if link["target"] == "main-navigation"
        ]
        self.assertEqual(len(nav_links), 1)
