from datetime import datetime, timedelta
from tumkwe_invest.ui.dashboard import (
    InsightCard, Dashboard, StockDashboard,
    create_apple_dashboard
)


class TestInsightCard:
    def test_init(self):
        card = InsightCard(
            "Revenue", "$1.5M", "Quarterly revenue", "+5%", "up"
        )
        
        assert card.title == "Revenue"
        assert card.value == "$1.5M"
        assert card.interpretation == "Quarterly revenue"
        assert card.trend == "+5%"
        assert card.trend_direction == "up"
        assert card.tooltip is None

    def test_add_tooltip(self):
        card = InsightCard("Revenue", "$1.5M", "Quarterly revenue")
        card.add_tooltip("Detailed explanation of revenue metric")
        
        assert card.tooltip == "Detailed explanation of revenue metric"

    def test_to_dict(self):
        card = InsightCard(
            "Revenue", "$1.5M", "Quarterly revenue", "+5%", "up"
        )
        card.add_tooltip("Detailed explanation")
        
        result = card.to_dict()
        assert result["title"] == "Revenue"
        assert result["value"] == "$1.5M"
        assert result["interpretation"] == "Quarterly revenue"
        assert result["trend"] == "+5%"
        assert result["trend_direction"] == "up"
        assert result["tooltip"] == "Detailed explanation"


class TestDashboard:
    def test_init(self):
        dashboard = Dashboard("AAPL", "Apple Inc.", "basic")
        
        assert dashboard.ticker == "AAPL"
        assert dashboard.company_name == "Apple Inc."
        assert dashboard.view_mode == "basic"
        assert dashboard.sections == {}
        assert isinstance(dashboard.last_updated, datetime)

    def test_add_section(self):
        dashboard = Dashboard("AAPL", "Apple Inc.")
        components = [{"type": "chart", "config": {}}]
        
        dashboard.add_section("price", "Price Information", components)
        
        assert "price" in dashboard.sections
        assert dashboard.sections["price"]["title"] == "Price Information"
        assert dashboard.sections["price"]["components"] == components

    def test_toggle_view_mode(self):
        dashboard = Dashboard("AAPL", "Apple Inc.", "basic")
        
        dashboard.toggle_view_mode()
        assert dashboard.view_mode == "advanced"
        
        dashboard.toggle_view_mode()
        assert dashboard.view_mode == "basic"

    def test_generate_dashboard_config(self):
        dashboard = Dashboard("AAPL", "Apple Inc.", "basic")
        dashboard.add_section("price", "Price Information", [])
        
        config = dashboard.generate_dashboard_config()
        
        assert config["ticker"] == "AAPL"
        assert config["company_name"] == "Apple Inc."
        assert config["view_mode"] == "basic"
        assert "price" in config["sections"]
        assert isinstance(config["last_updated"], str)  # Should be ISO format string


class TestStockDashboard:
    def test_init(self):
        dashboard = StockDashboard("AAPL", "Apple Inc.", "advanced")
        
        assert dashboard.ticker == "AAPL"
        assert dashboard.company_name == "Apple Inc."
        assert dashboard.view_mode == "advanced"
        assert dashboard.price_data == {}
        assert dashboard.technical_indicators == {}
        assert dashboard.fundamental_metrics == {}
        assert dashboard.sentiment_data == {}

    def test_set_price_data(self):
        dashboard = StockDashboard("AAPL", "Apple Inc.")
        dates = ["2023-01-01", "2023-01-02"]
        prices = [150.0, 155.0]
        volumes = [1000000, 1200000]
        
        dashboard.set_price_data(dates, prices, volumes)
        
        assert dashboard.price_data["dates"] == dates
        assert dashboard.price_data["prices"] == prices
        assert dashboard.price_data["volumes"] == volumes

    def test_set_technical_indicators(self):
        dashboard = StockDashboard("AAPL", "Apple Inc.")
        indicators = {
            "rsi": [45, 55],
            "macd": [0.5, 0.6]
        }
        
        dashboard.set_technical_indicators(indicators)
        
        assert dashboard.technical_indicators == indicators

    def test_set_fundamental_metrics(self):
        dashboard = StockDashboard("AAPL", "Apple Inc.")
        metrics = {
            "pe_ratio": {"value": 25.6, "industry_avg": 22.1},
            "roe": {"value": 0.35, "industry_avg": 0.28}
        }
        
        dashboard.set_fundamental_metrics(metrics)
        
        assert dashboard.fundamental_metrics == metrics

    def test_set_sentiment_data(self):
        dashboard = StockDashboard("AAPL", "Apple Inc.")
        sentiment = {
            "overall_score": 0.75,
            "summary": "Positive sentiment"
        }
        
        dashboard.set_sentiment_data(sentiment)
        
        assert dashboard.sentiment_data == sentiment

    def test_build_price_section(self):
        dashboard = StockDashboard("AAPL", "Apple Inc.")
        dates = ["2023-01-01", "2023-01-02"]
        prices = [150.0, 155.0]
        
        # With empty price data, section should not be created
        dashboard.build_price_section()
        assert "price" not in dashboard.sections
        
        # With price data, section should be created
        dashboard.set_price_data(dates, prices)
        dashboard.build_price_section()
        
        assert "price" in dashboard.sections
        assert dashboard.sections["price"]["title"] == "Price Information"
        assert len(dashboard.sections["price"]["components"]) == 2  # Chart and card
        
        # Check that chart is included
        assert dashboard.sections["price"]["components"][0]["type"] == "chart"
        # Check that card is included
        assert dashboard.sections["price"]["components"][1]["type"] == "card"

    def test_build_technical_section_basic_mode(self):
        dashboard = StockDashboard("AAPL", "Apple Inc.", "basic")
        
        # With empty indicators, section should not be created
        dashboard.build_technical_section()
        assert "technical" not in dashboard.sections
        
        # Add RSI indicator
        dashboard.set_technical_indicators({
            "rsi": [30, 45, 60],
            "macd": [0.1, 0.2, 0.3]
        })
        dashboard.build_technical_section()
        
        assert "technical" in dashboard.sections
        components = dashboard.sections["technical"]["components"]
        
        # In basic mode, should create simplified cards
        assert len(components) > 0
        # Check for RSI card
        rsi_cards = [c for c in components if c["type"] == "card" and 
                    "RSI" in c["config"]["title"]]
        assert len(rsi_cards) == 1
        
        # Check for technical health card
        health_cards = [c for c in components if c["type"] == "card" and 
                       "Health" in c["config"]["title"]]
        assert len(health_cards) == 1

    def test_build_technical_section_advanced_mode(self):
        dashboard = StockDashboard("AAPL", "Apple Inc.", "advanced")
        dates = ["2023-01-01", "2023-01-02"]
        
        dashboard.set_price_data(dates, [150.0, 155.0])
        dashboard.set_technical_indicators({
            "rsi": [45, 60],
            "macd": [0.1, 0.2],
            "moving_averages": {"MA50": [145, 150], "MA200": [140, 145]}
        })
        
        dashboard.build_technical_section()
        
        assert "technical" in dashboard.sections
        components = dashboard.sections["technical"]["components"]
        
        # In advanced mode, should create chart
        assert components[0]["type"] == "chart"
        
        # Should also create detailed cards for each indicator
        assert len(components) > 1

    def test_build_fundamental_section(self):
        dashboard = StockDashboard("AAPL", "Apple Inc.", "basic")
        
        # With empty metrics, section should not be created
        dashboard.build_fundamental_section()
        assert "fundamental" not in dashboard.sections
        
        # Add some fundamental metrics
        dashboard.set_fundamental_metrics({
            "pe_ratio": {"value": 25.6, "industry_avg": 22.1},
            "roe": {"value": 0.35, "industry_avg": 0.28}
        })
        dashboard.build_fundamental_section()
        
        assert "fundamental" in dashboard.sections
        components = dashboard.sections["fundamental"]["components"]
        
        # In basic mode, should create simplified cards
        assert len(components) > 0
        
        # Check for financial health card
        health_cards = [c for c in components if c["type"] == "card" and 
                       "Financial Health" in c["config"]["title"]]
        assert len(health_cards) == 1
        
        # Switch to advanced mode
        dashboard.view_mode = "advanced"
        dashboard.build_fundamental_section()
        
        assert "fundamental" in dashboard.sections
        advanced_components = dashboard.sections["fundamental"]["components"]
        
        # In advanced mode with valid data, should create chart
        assert advanced_components[0]["type"] == "chart"

    def test_build_sentiment_section(self):
        dashboard = StockDashboard("AAPL", "Apple Inc.")
        
        # With empty sentiment, section should not be created
        dashboard.build_sentiment_section()
        assert "sentiment" not in dashboard.sections
        
        # Add sentiment data
        dashboard.set_sentiment_data({
            "overall_score": 0.75,
            "summary": "Positive sentiment"
        })
        dashboard.build_sentiment_section()
        
        assert "sentiment" in dashboard.sections
        components = dashboard.sections["sentiment"]["components"]
        
        # Should include gauge
        gauge_components = [c for c in components if c["type"] == "gauge"]
        assert len(gauge_components) == 1
        
        # Should include sentiment card
        card_components = [c for c in components if c["type"] == "card"]
        assert len(card_components) == 1
        
        # Add news items and switch to advanced mode
        dashboard.view_mode = "advanced"
        dashboard.sentiment_data["news_items"] = [
            {"title": "Good news", "source": "News Inc.", "date": "2023-01-01", 
             "sentiment": 0.8, "url": "http://example.com"}
        ]
        dashboard.build_sentiment_section()
        
        assert "sentiment" in dashboard.sections
        advanced_components = dashboard.sections["sentiment"]["components"]
        
        # In advanced mode with news, should include news items
        news_components = [c for c in advanced_components if c["type"] == "news"]
        assert len(news_components) == 1

    def test_build_integrated_section(self):
        dashboard = StockDashboard("AAPL", "Apple Inc.", "basic")
        
        # In basic mode, section should not be created
        dashboard.build_integrated_section()
        assert "integrated" not in dashboard.sections
        
        # Switch to advanced mode but without integrated score
        dashboard.view_mode = "advanced"
        dashboard.build_integrated_section()
        assert "integrated" not in dashboard.sections
        
        # Add integrated score
        dashboard.sentiment_data["integrated_score"] = 75
        dashboard.build_integrated_section()
        
        assert "integrated" in dashboard.sections
        components = dashboard.sections["integrated"]["components"]
        assert len(components) == 1
        assert components[0]["type"] == "card"
        assert "Integrated Analysis Score" in components[0]["config"]["title"]

    def test_build_dashboard(self):
        dashboard = StockDashboard("AAPL", "Apple Inc.", "basic")
        
        # Set up some sample data
        dashboard.set_price_data(["2023-01-01", "2023-01-02"], [150, 155])
        dashboard.set_technical_indicators({"rsi": [45, 50]})
        dashboard.set_fundamental_metrics({"pe_ratio": {"value": 25, "industry_avg": 22}})
        dashboard.set_sentiment_data({"overall_score": 0.5})
        
        # Build the dashboard
        result = dashboard.build_dashboard()
        
        # Check that all sections are built
        assert "price" in result["sections"]
        assert "technical" in result["sections"]
        assert "fundamental" in result["sections"]
        assert "sentiment" in result["sections"]
        
        # Integrated analysis should not be in basic mode
        assert "integrated" not in result["sections"]
        
        # Switch to advanced mode
        dashboard.view_mode = "advanced"
        dashboard.sentiment_data["integrated_score"] = 75
        
        result = dashboard.build_dashboard()
        # Now integrated should be present
        assert "integrated" in result["sections"]

    def test_calculate_technical_health(self):
        dashboard = StockDashboard("AAPL", "Apple Inc.")
        
        # With no indicators, should return neutral
        health = dashboard._calculate_technical_health()
        assert health["status"] == "Neutral"
        
        # With positive indicators
        dashboard.set_technical_indicators({
            "rsi": [75],  # Overbought (positive)
            "macd": [0.5, 0.4],  # Rising (positive)
            "macd_signal": [0.3, 0.3],
            "moving_averages": {"MA50": [100, 105]}  # Rising (positive)
        })
        
        health = dashboard._calculate_technical_health()
        assert health["status"] in ["Strong", "Positive"]
        assert health["trend_direction"] == "up"
        
        # With negative indicators
        dashboard.set_technical_indicators({
            "rsi": [25],  # Oversold (negative)
            "macd": [0.2, 0.3],  # Falling (negative)
            "macd_signal": [0.4, 0.4],
            "moving_averages": {"MA50": [100, 95]}  # Falling (negative)
        })
        
        health = dashboard._calculate_technical_health()
        assert health["status"] in ["Weak", "Negative"]
        assert health["trend_direction"] == "down"

    def test_calculate_financial_health(self):
        dashboard = StockDashboard("AAPL", "Apple Inc.")
        
        # With no metrics, should return neutral
        health = dashboard._calculate_financial_health()
        assert health["status"] == "Neutral"
        
        # With strong metrics
        dashboard.set_fundamental_metrics({
            "roe": {"value": 0.35, "industry_avg": 0.28},  # Above industry (positive)
            "roa": {"value": 0.22, "industry_avg": 0.18},  # Above industry (positive)
            "pe_ratio": {"value": 20, "industry_avg": 25}  # Below industry for PE (positive)
        })
        
        health = dashboard._calculate_financial_health()
        assert health["status"] in ["Strong", "Positive"]
        assert health["trend_direction"] == "up"
        
        # With weak metrics
        dashboard.set_fundamental_metrics({
            "roe": {"value": 0.20, "industry_avg": 0.28},  # Below industry (negative)
            "roa": {"value": 0.15, "industry_avg": 0.18},  # Below industry (negative)
            "pe_ratio": {"value": 30, "industry_avg": 25}  # Above industry for PE (negative)
        })
        
        health = dashboard._calculate_financial_health()
        assert health["status"] in ["Weak", "Negative"]
        assert health["trend_direction"] == "down"

    def test_helper_interpretation_methods(self):
        dashboard = StockDashboard("AAPL", "Apple Inc.")
        
        # Test indicator interpretation
        rsi_interp = dashboard._get_indicator_interpretation("rsi", 25)
        assert "oversold" in rsi_interp.lower()
        
        rsi_interp = dashboard._get_indicator_interpretation("rsi", 75)
        assert "overbought" in rsi_interp.lower()
        
        rsi_interp = dashboard._get_indicator_interpretation("rsi", 50)
        assert "normal" in rsi_interp.lower()
        
        # Test unknown indicator
        unknown = dashboard._get_indicator_interpretation("unknown", 50)
        assert unknown == "Technical indicator"
        
        # Test fundamental interpretation
        pe_interp = dashboard._get_fundamental_interpretation("pe_ratio", 25, 20)
        assert "above" in pe_interp.lower()
        
        pe_interp = dashboard._get_fundamental_interpretation("pe_ratio", 15, 20)
        assert "below" in pe_interp.lower()
        
        # Test with no industry average
        no_avg = dashboard._get_fundamental_interpretation("pe_ratio", 15)
        assert "no industry comparison" in no_avg.lower()
        
        # Test fundamental tooltip
        pe_tooltip = dashboard._get_fundamental_tooltip("pe_ratio")
        assert "price-to-earnings" in pe_tooltip.lower()
        
        # Test unknown metric tooltip
        unknown = dashboard._get_fundamental_tooltip("unknown_metric")
        assert "financial metric" in unknown.lower()


class TestAppleDashboard:
    def test_create_apple_dashboard(self):
        dashboard = create_apple_dashboard("basic")
        
        # Check main structure
        assert dashboard["ticker"] == "AAPL"
        assert dashboard["company_name"] == "Apple Inc."
        assert dashboard["view_mode"] == "basic"
        assert "last_updated" in dashboard
        
        # Check required sections
        assert "price" in dashboard["sections"]
        assert "technical" in dashboard["sections"]
        assert "fundamental" in dashboard["sections"]
        assert "sentiment" in dashboard["sections"]
        
        # Test advanced mode
        dashboard_advanced = create_apple_dashboard("advanced")
        assert dashboard_advanced["view_mode"] == "advanced"
        assert "integrated" in dashboard_advanced["sections"]
