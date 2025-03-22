import json
from tumkwe_invest.ui.visualization import (
    StockChart, ComparisonChart, create_stock_price_chart,
    create_technical_indicators_chart, create_fundamental_comparison_chart,
    create_sentiment_gauge
)


class TestStockChart:
    def test_init(self):
        chart = StockChart("line", "dark")
        
        assert chart.chart_type == "line"
        assert chart.theme == "dark"
        assert chart.data == {}
        assert "colors" in chart.options
        assert chart.options["colors"]["background"] == "#121212"  # Dark theme

    def test_get_default_options(self):
        # Test light theme
        chart_light = StockChart(theme="light")
        light_options = chart_light._get_default_options()
        
        assert light_options["colors"]["background"] == "#FFFFFF"
        assert light_options["colors"]["text"] == "#202124"
        
        # Test high contrast theme
        chart_hc = StockChart(theme="high_contrast")
        hc_options = chart_hc._get_default_options()
        
        assert hc_options["colors"]["background"] == "#000000"
        assert hc_options["colors"]["positive"] == "#00E676"
        
        # Common options
        assert light_options["responsive"] is True
        assert hc_options["responsive"] is True
        assert "tooltip" in light_options
        assert "legend" in hc_options

    def test_add_price_data(self):
        chart = StockChart("line", "light")
        dates = ["2023-01-01", "2023-01-02", "2023-01-03"]
        prices = [100.0, 102.5, 101.2]
        
        chart.add_price_data(dates, prices, "Stock Price")
        
        assert chart.data["labels"] == dates
        assert len(chart.data["datasets"]) == 1
        assert chart.data["datasets"][0]["label"] == "Stock Price"
        assert chart.data["datasets"][0]["data"] == prices
        assert "borderColor" in chart.data["datasets"][0]
        
        # Test area chart fill
        area_chart = StockChart("area", "light")
        area_chart.add_price_data(dates, prices)
        assert area_chart.data["datasets"][0]["fill"] is True

    def test_add_trend_indicators(self):
        chart = StockChart()
        # First set up some base data
        chart.add_price_data(["2023-01-01"], [100.0])
        
        indicators = {
            "MA50": [98.0, 99.0, 100.5],
            "RSI": [45.0, 52.0, 48.0]
        }
        
        chart.add_trend_indicators(indicators)
        
        # Should now have 3 datasets (1 original + 2 indicators)
        assert len(chart.data["datasets"]) == 3
        
        # Check that the indicators were added correctly
        indicator_labels = [ds["label"] for ds in chart.data["datasets"][1:]]
        assert "MA50" in indicator_labels
        assert "RSI" in indicator_labels
        
        # Test with custom colors
        chart = StockChart()
        chart.add_price_data(["2023-01-01"], [100.0])
        chart.add_trend_indicators(indicators, {"MA50": "#FF0000"})
        
        # Find the MA50 dataset
        for ds in chart.data["datasets"]:
            if ds["label"] == "MA50":
                assert ds["borderColor"] == "#FF0000"

    def test_get_color_by_index(self):
        chart = StockChart()
        
        color0 = chart._get_color_by_index(0)
        color1 = chart._get_color_by_index(1)
        color8 = chart._get_color_by_index(8)  # Should wrap around to index 0
        
        assert color0 == "#4285F4"  # First color
        assert color1 == "#EA4335"  # Second color
        assert color8 == color0  # Should wrap around

    def test_adjust_opacity(self):
        chart = StockChart()
        
        rgba = chart._adjust_opacity("#FF0000", 0.5)
        assert rgba == "rgba(255, 0, 0, 0.5)"
        
        rgba2 = chart._adjust_opacity("#00FF00", 0.8)
        assert rgba2 == "rgba(0, 255, 0, 0.8)"

    def test_generate_config(self):
        chart = StockChart("line", "light")
        dates = ["2023-01-01", "2023-01-02"]
        prices = [100.0, 102.5]
        chart.add_price_data(dates, prices)
        
        config = chart.generate_config()
        
        assert config["type"] == "line"
        assert config["data"] == chart.data
        assert config["options"] == chart.options

    def test_to_json(self):
        chart = StockChart()
        chart.add_price_data(["2023-01-01"], [100.0])
        
        json_str = chart.to_json()
        parsed = json.loads(json_str)
        
        assert isinstance(parsed, dict)
        assert "type" in parsed
        assert "data" in parsed
        assert "options" in parsed


class TestComparisonChart:
    def test_init(self):
        chart = ComparisonChart("bar")
        
        assert chart.chart_type == "bar"
        assert chart.data == {}
        assert "responsive" in chart.options
        assert "scales" in chart.options
        assert "plugins" in chart.options

    def test_add_comparison_data(self):
        chart = ComparisonChart()
        labels = ["Metric 1", "Metric 2", "Metric 3"]
        datasets = [
            {
                "label": "Company A",
                "data": [10, 20, 30],
                "backgroundColor": "rgba(255, 0, 0, 0.5)"
            },
            {
                "label": "Company B",
                "data": [15, 25, 35],
                "backgroundColor": "rgba(0, 255, 0, 0.5)"
            }
        ]
        
        chart.add_comparison_data(labels, datasets)
        
        assert chart.data["labels"] == labels
        assert chart.data["datasets"] == datasets

    def test_generate_config(self):
        chart = ComparisonChart("radar")
        chart.add_comparison_data(["A", "B"], [{"label": "Test", "data": [1, 2]}])
        
        config = chart.generate_config()
        
        assert config["type"] == "radar"
        assert config["data"] == chart.data
        assert config["options"] == chart.options

    def test_to_json(self):
        chart = ComparisonChart()
        chart.add_comparison_data(["A", "B"], [{"label": "Test", "data": [1, 2]}])
        
        json_str = chart.to_json()
        parsed = json.loads(json_str)
        
        assert isinstance(parsed, dict)
        assert "data" in parsed
        assert parsed["data"]["labels"] == ["A", "B"]


class TestHelperFunctions:
    def test_create_stock_price_chart(self):
        dates = ["2023-01-01", "2023-01-02", "2023-01-03"]
        prices = [100.0, 102.5, 101.2]
        moving_averages = {"MA50": [99.0, 100.5, 101.0]}
        
        # Test minimal version
        basic_chart = create_stock_price_chart(dates, prices)
        assert basic_chart["type"] == "line"
        assert len(basic_chart["data"]["datasets"]) == 1
        
        # Test with additional data
        full_chart = create_stock_price_chart(
            dates, prices, moving_averages, [1000, 1200, 1100], "dark"
        )
        assert len(full_chart["data"]["datasets"]) > 1
        # Check that moving averages were added
        found_ma = False
        for dataset in full_chart["data"]["datasets"]:
            if dataset.get("label") == "MA50":
                found_ma = True
                break
        assert found_ma

    def test_create_technical_indicators_chart(self):
        dates = ["2023-01-01", "2023-01-02", "2023-01-03"]
        indicators = {
            "rsi": [45, 55, 60],
            "macd": [0.2, 0.3, 0.4]
        }
        
        chart = create_technical_indicators_chart(dates, indicators)
        
        assert chart["type"] == "line"
        # We should have datasets for each indicator
        assert len(chart["data"]["datasets"]) == len(indicators)
        # Check indicator names
        indicator_names = [ds["label"] for ds in chart["data"]["datasets"]]
        assert "rsi" in indicator_names
        assert "macd" in indicator_names

    def test_create_fundamental_comparison_chart(self):
        metrics = ["P/E", "ROE", "Debt/Equity"]
        stock_values = [15.2, 0.22, 0.8]
        benchmark_values = [18.5, 0.18, 1.2]
        industry_values = [16.8, 0.20, 1.0]
        
        # Test with industry values
        chart = create_fundamental_comparison_chart(
            metrics, stock_values, benchmark_values, industry_values
        )
        
        assert chart["type"] == "bar"
        assert chart["data"]["labels"] == metrics
        assert len(chart["data"]["datasets"]) == 3  # Stock, Benchmark, Industry
        
        # Test without industry values
        chart_no_industry = create_fundamental_comparison_chart(
            metrics, stock_values, benchmark_values
        )
        
        assert len(chart_no_industry["data"]["datasets"]) == 2  # Stock, Benchmark

    def test_create_sentiment_gauge(self):
        # Test positive sentiment
        positive_gauge = create_sentiment_gauge(0.75)
        
        assert positive_gauge["type"] == "gauge"
        assert positive_gauge["data"]["datasets"][0]["value"] == 0.75
        assert positive_gauge["data"]["datasets"][0]["minValue"] == -1.0
        assert positive_gauge["data"]["datasets"][0]["maxValue"] == 1.0
        
        # Check that color changes with sentiment value
        very_negative = create_sentiment_gauge(-0.8)
        negative = create_sentiment_gauge(-0.5)
        neutral = create_sentiment_gauge(0)
        positive = create_sentiment_gauge(0.5)
        very_positive = create_sentiment_gauge(0.8)
        
        # All should have different colors
        colors = [
            very_negative["data"]["datasets"][0]["backgroundColor"],
            negative["data"]["datasets"][0]["backgroundColor"],
            neutral["data"]["datasets"][0]["backgroundColor"],
            positive["data"]["datasets"][0]["backgroundColor"],
            very_positive["data"]["datasets"][0]["backgroundColor"]
        ]
        assert len(set(colors)) == 5  # All 5 should be different
