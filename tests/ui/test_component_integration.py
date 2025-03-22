"""
Integration tests for UI components working together in Tumkwe Invest.
"""

from tumkwe_invest.ui.components import (
    Card, Button, Tooltip, Chart, SectionLayout, ToggleSwitch
)
from tumkwe_invest.ui.visualization import StockChart, create_sentiment_gauge
from tumkwe_invest.ui.dashboard import InsightCard


class TestComponentCombinations:
    def test_card_with_button(self):
        """Test creating a card with button actions."""
        # Create a card with buttons in the content
        card = Card(title="Action Card", component_id="action-card")
        
        # Create buttons that will be used in the card
        primary_btn = Button("Accept", "primary", "medium", "accept-btn")
        secondary_btn = Button("Cancel", "secondary", "medium", "cancel-btn")
        
        # Set the card content to include buttons
        card.set_content({
            "text": "Please confirm your choice",
            "actions": [
                primary_btn.to_dict(),
                secondary_btn.to_dict()
            ]
        })
        
        # Convert to dictionary representation
        result = card.to_dict()
        
        # Verify the integrated components
        assert result["title"] == "Action Card"
        assert len(result["content"]["actions"]) == 2
        assert result["content"]["actions"][0]["label"] == "Accept"
        assert result["content"]["actions"][1]["label"] == "Cancel"
        assert "button-primary" in result["content"]["actions"][0]["classes"]
    
    def test_section_with_mixed_components(self):
        """Test section layout with various components."""
        # Create a section with multiple component types
        section = SectionLayout("Dashboard Overview", component_id="overview-section")
        
        # Add a card
        card = Card("Summary", "Performance overview")
        section.add_component(card.to_dict())
        
        # Add a toggle
        toggle = ToggleSwitch("Show Details", component_id="details-toggle")
        section.add_component(toggle.to_dict())
        
        # Add a button
        button = Button("Refresh", "secondary", component_id="refresh-btn")
        section.add_component(button.to_dict())
        
        # Convert to dictionary
        result = section.to_dict()
        
        # Verify the integrated components
        assert result["title"] == "Dashboard Overview"
        assert len(result["components"]) == 3
        assert result["components"][0]["type"] == "card"
        assert result["components"][1]["type"] == "toggleSwitch"
        assert result["components"][2]["type"] == "button"
    
    def test_tooltip_with_button(self):
        """Test attaching tooltip to a button."""
        # Create button
        button = Button("Help", "info", "small", "help-btn")
        
        # Create tooltip
        tooltip = Tooltip(
            content="Click for additional assistance",
            position="bottom",
            component_id="help-tooltip"
        )
        
        # Set tooltip target
        tooltip.set_attribute("data-target", button.component_id)
        
        # Convert both to dictionary
        button_dict = button.to_dict()
        tooltip_dict = tooltip.to_dict()
        
        # Verify connection
        assert tooltip_dict["attributes"]["data-target"] == button_dict["id"]
        assert tooltip_dict["position"] == "bottom"
    
    def test_chart_in_card(self):
        """Test embedding a chart in a card."""
        # Create a stock chart
        chart_config = StockChart("line")
        chart_config.add_price_data(
            ["2023-01-01", "2023-01-02"],
            [100.0, 105.0],
            "Stock Price"
        )
        
        # Create a chart component
        chart = Chart(
            chart_config=chart_config.generate_config(),
            height="300px",
            component_id="stock-chart"
        )
        
        # Create a card containing the chart
        card = Card(
            title="Stock Performance",
            content=chart.to_dict(),
            component_id="performance-card"
        )
        
        # Convert to dictionary
        result = card.to_dict()
        
        # Verify the embedded chart
        assert result["title"] == "Stock Performance"
        assert result["content"]["type"] == "chart"
        assert result["content"]["chartConfig"]["type"] == "line"
        assert result["content"]["height"] == "300px"
        assert "chart" in result["content"]["classes"]
    
    def test_insight_card_in_section(self):
        """Test adding insight cards to a section."""
        # Create insight cards
        revenue_card = InsightCard(
            "Revenue",
            "$1.5M",
            "Quarterly revenue",
            "+5%",
            "up"
        )
        revenue_card.add_tooltip("Revenue increased by 5% compared to last quarter")
        
        profit_card = InsightCard(
            "Profit",
            "$320K",
            "Quarterly profit",
            "-2%",
            "down"
        )
        profit_card.add_tooltip("Profit decreased due to increased expenses")
        
        # Create a section with these cards
        section = SectionLayout("Financial Overview", component_id="finance-section")
        section.add_component({"type": "card", "config": revenue_card.to_dict()})
        section.add_component({"type": "card", "config": profit_card.to_dict()})
        
        # Convert to dictionary
        result = section.to_dict()
        
        # Verify the section with insight cards
        assert result["title"] == "Financial Overview"
        assert len(result["components"]) == 2
        assert result["components"][0]["config"]["title"] == "Revenue"
        assert result["components"][1]["config"]["trend_direction"] == "down"


class TestChartIntegrations:
    def test_sentiment_gauge_in_card(self):
        """Test embedding a sentiment gauge in a card."""
        # Create a sentiment gauge
        gauge_config = create_sentiment_gauge(0.75)
        
        # Create a chart component for the gauge
        chart = Chart(
            chart_config=gauge_config,
            height="200px",
            width="200px",
            component_id="sentiment-gauge"
        )
        
        # Create a card containing the gauge
        card = Card(
            title="Market Sentiment",
            content={
                "chart": chart.to_dict(),
                "interpretation": "Strongly positive market sentiment"
            },
            component_id="sentiment-card"
        )
        
        # Convert to dictionary
        result = card.to_dict()
        
        # Verify the embedded gauge
        assert result["title"] == "Market Sentiment"
        assert result["content"]["chart"]["chartConfig"]["type"] == "gauge"
        assert result["content"]["chart"]["height"] == "200px"
        assert abs(result["content"]["chart"]["chartConfig"]["data"]["datasets"][0]["value"] - 0.75) < 0.001
        assert result["content"]["interpretation"] == "Strongly positive market sentiment"


class TestFixtureComponents:
    def test_sample_card_structure(self, sample_card):
        """Test the structure of the sample card fixture."""
        card_dict = sample_card.to_dict()
        
        assert card_dict["id"] == "sample-card"
        assert card_dict["title"] == "Sample Card"
        assert "custom-card" in card_dict["classes"]
        assert "card" in card_dict["classes"]
        assert card_dict["footer"] == "Card footer"
        assert len(card_dict["headerActions"]) == 1
        assert card_dict["headerActions"][0]["icon"] == "info"
    
    def test_sample_stock_chart_structure(self, sample_stock_chart):
        """Test the structure of the sample stock chart fixture."""
        config = sample_stock_chart.generate_config()
        
        assert config["type"] == "line"
        assert len(config["data"]["labels"]) == 5  # 5 dates
        assert len(config["data"]["datasets"]) == 3  # Price + 2 indicators
        assert config["data"]["datasets"][0]["label"] == "Stock Price"
        
        # Check indicators
        indicator_labels = [ds["label"] for ds in config["data"]["datasets"]]
        assert "MA50" in indicator_labels
        assert "RSI" in indicator_labels
    
    def test_sample_dashboard_structure(self, sample_dashboard):
        """Test building a dashboard from the sample dashboard fixture."""
        # Build the dashboard
        dashboard_config = sample_dashboard.build_dashboard()
        
        # Verify basic structure
        assert dashboard_config["ticker"] == "TSLA"
        assert dashboard_config["company_name"] == "Tesla, Inc."
        assert dashboard_config["view_mode"] == "basic"
        
        # Verify sections are built
        assert "price" in dashboard_config["sections"]
        assert "technical" in dashboard_config["sections"] 
        assert "fundamental" in dashboard_config["sections"]
        assert "sentiment" in dashboard_config["sections"]
        
        # Check price section components
        price_components = dashboard_config["sections"]["price"]["components"]
        assert len(price_components) == 2  # Chart and card
        assert price_components[0]["type"] == "chart"
        assert price_components[1]["type"] == "card"
        
        # Check sentiment section
        sentiment_components = dashboard_config["sections"]["sentiment"]["components"]
        gauge_components = [c for c in sentiment_components if c["type"] == "gauge"]
        assert len(gauge_components) == 1
