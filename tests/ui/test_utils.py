import re
from datetime import date, datetime

from tumkwe_invest.ui.utils import (
    AccessibilityUtils,
    convert_to_frontend_format,
    create_theme_config,
    format_currency,
    format_date,
    format_number,
    format_percent,
    format_timeframe,
    generate_color_palette,
    get_contrast_text_color,
    get_trend_color,
    sanitize_html,
    simplify_large_number,
    truncate_text,
)


class TestFormattingFunctions:
    def test_format_currency(self):
        # Due to locale dependencies, just check structure
        result = format_currency(1234.56)
        assert "$" in result
        assert "1" in result
        assert "234" in result
        assert "56" in result

        # Test with custom currency symbol
        result_euro = format_currency(1234.56, "€")
        assert "€" in result_euro

        # Test integer value
        result_int = format_currency(1000)
        assert "$" in result_int
        assert "1" in result_int
        assert "000" in result_int

    def test_format_number(self):
        # Due to locale dependencies, just check structure
        result = format_number(1234.56, 2)
        assert "1" in result
        assert "234" in result
        assert "56" in result

        # Test with different precision
        result_precision = format_number(1234.56789, 4)
        assert ".5678" in result_precision or "5678" in result_precision

        # Test integer value
        result_int = format_number(1000)
        assert "1" in result_int
        assert "000" in result_int

    def test_format_percent(self):
        # Test basic functionality
        assert format_percent(0.1234, 2) == "12.34%"

        # Test with sign
        assert format_percent(0.1234, 2, True) == "+12.34%"
        assert format_percent(-0.1234, 2, True) == "-12.34%"

        # Test zero
        assert format_percent(0, 0) == "0%"

        # Test precision
        assert format_percent(0.1, 0) == "10%"
        assert format_percent(0.1, 1) == "10.0%"

    def test_format_date(self):
        # Test with datetime object
        dt = datetime(2023, 4, 15, 10, 30, 0)
        assert format_date(dt) == "2023-04-15"
        assert format_date(dt, "%d/%m/%Y") == "15/04/2023"

        # Test with date object
        d = date(2023, 4, 15)
        assert format_date(d) == "2023-04-15"

        # Test with string
        assert format_date("2023-04-15T10:30:00Z") == "2023-04-15"

        # Test with invalid string (should return original)
        assert format_date("invalid date") == "invalid date"

    def test_format_timeframe(self):
        assert format_timeframe("1d") == "Daily"
        assert format_timeframe("1w") == "Weekly"
        assert format_timeframe("1m") == "Monthly"
        assert format_timeframe("max") == "Maximum"

        # Test unknown timeframe (should return original)
        assert format_timeframe("2h") == "2h"

    def test_truncate_text(self):
        # Test text within limit
        short_text = "This is a short text"
        assert truncate_text(short_text, 100) == short_text

        # Test text beyond limit
        long_text = "This is a very long text that should be truncated because it exceeds the maximum length"
        truncated = truncate_text(long_text, 20)
        assert len(truncated) == 20  # 17 chars + 3 dots
        assert truncated.endswith("...")

        # Test edge case
        assert len(truncate_text(long_text, 5)) == 5
        assert truncate_text("12345", 5) == "12345"  # No truncation needed

    def test_sanitize_html(self):
        # Test script tag removal
        html = "<p>Good</p><script>alert('bad')</script><p>More good</p>"
        sanitized = sanitize_html(html)
        assert "<script>" not in sanitized
        assert "alert" not in sanitized
        assert "<p>Good</p>" in sanitized
        assert "<p>More good</p>" in sanitized

        # Test onclick attribute removal
        html = '<button onclick="evil()">Click me</button>'
        sanitized = sanitize_html(html)
        assert "onclick" not in sanitized
        assert "Click me" in sanitized

        # Test other on* attributes
        html = "<div onmouseover='evil()' onload=\"evil()\">Content</div>"
        sanitized = sanitize_html(html)
        assert "onmouseover" not in sanitized
        assert "onload" not in sanitized
        assert "Content" in sanitized

    def test_generate_color_palette(self):
        # Test generating palette
        palette = generate_color_palette("#FF0000", 3)
        assert len(palette) == 3
        assert palette[0] == "#ff0000"  # Base color
        assert palette[0] != palette[1]  # Should be different colors
        assert palette[1] != palette[2]

        # Check that all colors are valid hex
        for color in palette:
            assert re.match(r"^#[0-9a-f]{6}$", color)

        # Test edge case - 1 color
        single_palette = generate_color_palette("#00FF00", 1)
        assert len(single_palette) == 1
        assert single_palette[0] == "#00ff00"

    def test_get_trend_color(self):
        # Test positive trend
        assert get_trend_color(0.1) == "#34A853"  # Green in light theme

        # Test negative trend
        assert get_trend_color(-0.1) == "#EA4335"  # Red in light theme

        # Test neutral (within threshold)
        assert get_trend_color(0.02) == "#6C757D"  # Gray in light theme

        # Test dark theme
        assert get_trend_color(0.1, theme="dark") == "#00C853"  # Green in dark theme
        assert get_trend_color(-0.1, theme="dark") == "#FF5252"  # Red in dark theme

    def test_get_contrast_text_color(self):
        # Dark background should return white text
        assert get_contrast_text_color("#000000") == "#FFFFFF"
        assert get_contrast_text_color("#0000FF") == "#FFFFFF"
        assert get_contrast_text_color("#123456") == "#FFFFFF"

        # Light background should return black text
        assert get_contrast_text_color("#FFFFFF") == "#000000"
        assert get_contrast_text_color("#FFFF00") == "#000000"
        assert get_contrast_text_color("#E0E0E0") == "#000000"

    def test_simplify_large_number(self):
        # Small numbers unchanged
        assert simplify_large_number(123) == "123"
        assert simplify_large_number(999) == "999"

        # Thousands
        assert simplify_large_number(1000) == "1K"
        assert simplify_large_number(1500) == "1.5K"

        # Millions
        assert simplify_large_number(1000000) == "1M"
        assert simplify_large_number(2500000) == "2.5M"

        # Billions
        assert simplify_large_number(1000000000) == "1B"

        # Trillions
        assert simplify_large_number(1000000000000) == "1T"

        # Check that .0 is removed
        assert simplify_large_number(2000000) == "2M"  # Not "2.0M"


class TestThemeConfig:
    def test_create_theme_config(self):
        # Test light theme
        light_theme = create_theme_config("Light Theme", False, "#4285F4")

        assert light_theme["name"] == "Light Theme"
        assert light_theme["dark"] is False
        assert light_theme["colors"]["primary"] == "#4285F4"
        assert light_theme["colors"]["background"] == "#FFFFFF"
        assert light_theme["colors"]["text"] == "#202124"
        assert len(light_theme["colors"]["palette"]) == 5

        # Test dark theme
        dark_theme = create_theme_config("Dark Theme", True, "#6200EE")

        assert dark_theme["name"] == "Dark Theme"
        assert dark_theme["dark"] is True
        assert dark_theme["colors"]["primary"] == "#6200EE"
        assert dark_theme["colors"]["background"] == "#121212"
        assert dark_theme["colors"]["text"] == "#FFFFFF"


class TestDataConversion:
    def test_convert_to_frontend_format(self):
        # Test datetime conversion
        dt = datetime(2023, 4, 15, 10, 30, 0)
        converted_dt = convert_to_frontend_format(dt)
        assert converted_dt == dt.isoformat()

        # Test date conversion
        d = date(2023, 4, 15)
        converted_d = convert_to_frontend_format(d)
        assert converted_d == d.isoformat()

        # Test dictionary conversion
        test_dict = {"date": dt, "value": 123, "name": "Test"}
        converted_dict = convert_to_frontend_format(test_dict)
        assert converted_dict["date"] == dt.isoformat()
        assert converted_dict["value"] == 123
        assert converted_dict["name"] == "Test"

        # Test list conversion
        test_list = [dt, d, 123, "Test"]
        converted_list = convert_to_frontend_format(test_list)
        assert converted_list[0] == dt.isoformat()
        assert converted_list[1] == d.isoformat()
        assert converted_list[2] == 123
        assert converted_list[3] == "Test"

        # Test nested structures
        nested = {"data": {"dates": [dt, d], "values": [1, 2, 3]}}
        converted_nested = convert_to_frontend_format(nested)
        assert converted_nested["data"]["dates"][0] == dt.isoformat()
        assert converted_nested["data"]["dates"][1] == d.isoformat()
        assert converted_nested["data"]["values"] == [1, 2, 3]


class TestAccessibilityUtils:
    def test_get_aria_labels(self):
        utils = AccessibilityUtils()

        # Test chart
        chart_aria = utils.get_aria_labels("chart", {"title": "Stock Performance"})
        assert chart_aria["aria-label"] == "Chart: Stock Performance"
        assert chart_aria["role"] == "img"

        # Test chart with no title
        chart_aria_no_title = utils.get_aria_labels("chart", {})
        assert chart_aria_no_title["aria-label"] == "Chart: Data visualization"

        # Test metric
        metric_aria = utils.get_aria_labels(
            "metric", {"title": "Revenue", "value": "$1M"}
        )
        assert metric_aria["aria-label"] == "Revenue: $1M"

        # Test button
        button_aria = utils.get_aria_labels("button", {"disabled": True})
        assert button_aria["role"] == "button"
        assert button_aria["aria-disabled"] == "true"

        # Test toggle
        toggle_aria = utils.get_aria_labels("toggle", {"checked": True})
        assert toggle_aria["role"] == "switch"
        assert toggle_aria["aria-checked"] == "true"

        # Test toggle unchecked
        toggle_off_aria = utils.get_aria_labels("toggle", {"checked": False})
        assert toggle_off_aria["aria-checked"] == "false"

    def test_generate_skip_links(self):
        utils = AccessibilityUtils()
        links = utils.generate_skip_links()

        assert isinstance(links, list)
        assert len(links) >= 2  # Should have at least 2 skip links

        # Check structure
        for link in links:
            assert "id" in link
            assert "target" in link
            assert "text" in link

    def test_get_keyboard_shortcuts(self):
        utils = AccessibilityUtils()
        shortcuts = utils.get_keyboard_shortcuts()

        assert isinstance(shortcuts, dict)
        assert len(shortcuts) > 0

        # Check that it includes expected shortcuts
        assert "?" in shortcuts
        assert "t" in shortcuts
        assert "Esc" in shortcuts
