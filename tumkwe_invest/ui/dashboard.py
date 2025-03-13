"""
Dashboard components for Tumkwe Invest.

This module provides classes and functions to create comprehensive dashboards
that summarize technical, fundamental, and sentiment insights.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta

from .visualization import (
    create_stock_price_chart,
    create_technical_indicators_chart,
    create_fundamental_comparison_chart,
    create_sentiment_gauge
)


class InsightCard:
    """A card component to display a single insight or metric."""
    
    def __init__(self, title: str, value: Any, 
                interpretation: str, trend: Optional[str] = None, 
                trend_direction: Optional[str] = None):
        """
        Initialize an insight card.
        
        Args:
            title: Title/name of the metric
            value: Value of the metric
            interpretation: Simple explanation of what the metric means
            trend: Optional trend indication (e.g., "+2.5% MoM")
            trend_direction: Optional direction ('up', 'down', 'neutral')
        """
        self.title = title
        self.value = value
        self.interpretation = interpretation
        self.trend = trend
        self.trend_direction = trend_direction
        self.tooltip = None
    
    def add_tooltip(self, detailed_explanation: str) -> None:
        """Add a detailed tooltip explanation to the card."""
        self.tooltip = detailed_explanation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the card to a dictionary for rendering."""
        return {
            "title": self.title,
            "value": self.value,
            "interpretation": self.interpretation,
            "trend": self.trend,
            "trend_direction": self.trend_direction,
            "tooltip": self.tooltip
        }


class Dashboard:
    """Main dashboard class for organizing and displaying stock insights."""
    
    def __init__(self, ticker: str, company_name: str, view_mode: str = "basic"):
        """
        Initialize a dashboard.
        
        Args:
            ticker: Stock ticker symbol
            company_name: Company name
            view_mode: 'basic' or 'advanced'
        """
        self.ticker = ticker
        self.company_name = company_name
        self.view_mode = view_mode  # 'basic' or 'advanced'
        self.sections = {}
        self.last_updated = datetime.now()
    
    def add_section(self, section_id: str, title: str, 
                   components: List[Dict[str, Any]]) -> None:
        """
        Add a section to the dashboard.
        
        Args:
            section_id: Unique identifier for the section
            title: Section title
            components: List of components in the section
        """
        self.sections[section_id] = {
            "title": title,
            "components": components
        }
    
    def toggle_view_mode(self) -> None:
        """Toggle between basic and advanced view modes."""
        self.view_mode = "advanced" if self.view_mode == "basic" else "basic"
    
    def generate_dashboard_config(self) -> Dict[str, Any]:
        """Generate the full dashboard configuration."""
        return {
            "ticker": self.ticker,
            "company_name": self.company_name,
            "view_mode": self.view_mode,
            "sections": self.sections,
            "last_updated": self.last_updated.isoformat()
        }


class StockDashboard(Dashboard):
    """Specific dashboard implementation for stock analysis."""
    
    def __init__(self, ticker: str, company_name: str, view_mode: str = "basic"):
        """Initialize a stock-specific dashboard."""
        super().__init__(ticker, company_name, view_mode)
        self.price_data = {}
        self.technical_indicators = {}
        self.fundamental_metrics = {}
        self.sentiment_data = {}
        
    def set_price_data(self, dates: List[str], prices: List[float], 
                      volumes: Optional[List[int]] = None) -> None:
        """Set historical price data for the dashboard."""
        self.price_data = {
            "dates": dates,
            "prices": prices,
            "volumes": volumes
        }
        
    def set_technical_indicators(self, indicators: Dict[str, List[float]]) -> None:
        """Set technical indicators data for the dashboard."""
        self.technical_indicators = indicators
        
    def set_fundamental_metrics(self, metrics: Dict[str, Dict[str, float]]) -> None:
        """Set fundamental metrics data for the dashboard."""
        self.fundamental_metrics = metrics
        
    def set_sentiment_data(self, sentiment: Dict[str, Any]) -> None:
        """Set sentiment analysis data for the dashboard."""
        self.sentiment_data = sentiment
        
    def build_price_section(self) -> None:
        """Build the price chart section of the dashboard."""
        if not self.price_data:
            return
            
        price_chart = create_stock_price_chart(
            self.price_data["dates"],
            self.price_data["prices"],
            moving_averages=self.technical_indicators.get("moving_averages", None),
            volume=self.price_data.get("volumes", None)
        )
        
        # Create price insight cards
        current_price = self.price_data["prices"][-1] if self.price_data["prices"] else 0
        prev_price = self.price_data["prices"][-2] if len(self.price_data["prices"]) > 1 else current_price
        price_change = current_price - prev_price
        price_change_pct = (price_change / prev_price * 100) if prev_price != 0 else 0
        
        price_card = InsightCard(
            title="Current Price",
            value=f"${current_price:.2f}",
            interpretation="Latest trading price",
            trend=f"{price_change_pct:+.2f}%",
            trend_direction="up" if price_change >= 0 else "down"
        )
        
        components = [
            {"type": "chart", "config": price_chart},
            {"type": "card", "config": price_card.to_dict()}
        ]
        
        self.add_section("price", "Price Information", components)
        
    def build_technical_section(self) -> None:
        """Build the technical analysis section of the dashboard."""
        if not self.technical_indicators:
            return
            
        # Create a simplified view for basic mode
        if self.view_mode == "basic":
            # Extract key technical indicators for simplified view
            key_indicators = {}
            
            if "rsi" in self.technical_indicators:
                key_indicators["RSI"] = self.technical_indicators["rsi"]
            
            if "macd" in self.technical_indicators:
                key_indicators["MACD"] = self.technical_indicators["macd"]
            
            # Create insight cards
            components = []
            
            # Add RSI card if available
            if "rsi" in self.technical_indicators:
                current_rsi = self.technical_indicators["rsi"][-1]
                rsi_status = "Oversold" if current_rsi < 30 else "Overbought" if current_rsi > 70 else "Neutral"
                
                rsi_card = InsightCard(
                    title="RSI",
                    value=f"{current_rsi:.1f}",
                    interpretation=f"Currently {rsi_status}",
                    trend_direction="down" if current_rsi < 30 else "up" if current_rsi > 70 else "neutral"
                )
                rsi_card.add_tooltip("Relative Strength Index measures momentum. RSI below 30 indicates oversold conditions, while above 70 indicates overbought conditions.")
                components.append({"type": "card", "config": rsi_card.to_dict()})
            
            # Create a "Stock Health" card for basic users
            technical_health = self._calculate_technical_health()
            health_card = InsightCard(
                title="Stock Technical Health",
                value=technical_health["status"],
                interpretation=technical_health["interpretation"],
                trend_direction=technical_health["trend_direction"]
            )
            health_card.add_tooltip("Technical Health is a simplified indicator combining multiple technical signals to give an overall assessment of price momentum.")
            components.append({"type": "card", "config": health_card.to_dict()})
            
        else:  # Advanced mode
            # Create comprehensive technical charts
            if self.price_data.get("dates"):
                tech_chart = create_technical_indicators_chart(
                    self.price_data["dates"],
                    self.technical_indicators
                )
                components = [{"type": "chart", "config": tech_chart}]
                
                # Add detailed technical cards for advanced users
                for indicator_name, values in self.technical_indicators.items():
                    if not values:
                        continue
                        
                    current_value = values[-1]
                    prev_value = values[-2] if len(values) > 1 else current_value
                    change = current_value - prev_value
                    
                    card = InsightCard(
                        title=indicator_name.upper(),
                        value=f"{current_value:.2f}",
                        interpretation=self._get_indicator_interpretation(indicator_name, current_value),
                        trend=f"{change:+.2f}",
                        trend_direction="up" if change >= 0 else "down"
                    )
                    components.append({"type": "card", "config": card.to_dict()})
        
        self.add_section("technical", "Technical Analysis", components)
    
    def build_fundamental_section(self) -> None:
        """Build the fundamental analysis section of the dashboard."""
        if not self.fundamental_metrics:
            return
        
        # For basic view, simplify and focus on key metrics
        if self.view_mode == "basic":
            components = []
            
            # Create a simplified "Company Financial Health" card
            financial_health = self._calculate_financial_health()
            health_card = InsightCard(
                title="Company Financial Health",
                value=financial_health["status"],
                interpretation=financial_health["interpretation"],
                trend_direction=financial_health["trend_direction"]
            )
            health_card.add_tooltip("Financial Health combines multiple fundamental metrics to give an overall assessment of the company's financial position.")
            components.append({"type": "card", "config": health_card.to_dict()})
            
            # Add P/E ratio with simplified explanation
            if "pe_ratio" in self.fundamental_metrics:
                pe_value = self.fundamental_metrics["pe_ratio"].get("value", 0)
                industry_pe = self.fundamental_metrics["pe_ratio"].get("industry_avg", 0)
                
                pe_status = "Lower than industry average" if pe_value < industry_pe else "Higher than industry average"
                if abs(pe_value - industry_pe) / industry_pe < 0.1:  # Within 10%
                    pe_status = "Near industry average"
                
                pe_card = InsightCard(
                    title="Price-to-Earnings",
                    value=f"{pe_value:.1f}x",
                    interpretation=pe_status,
                    trend_direction="neutral"
                )
                pe_card.add_tooltip("Price-to-Earnings (P/E) ratio compares the company's share price to its earnings. Lower values may indicate the stock is undervalued, while higher values might suggest overvaluation.")
                components.append({"type": "card", "config": pe_card.to_dict()})
            
        else:  # Advanced view
            # Create comparison chart for fundamentals
            metrics = []
            stock_values = []
            industry_values = []
            
            for name, data in self.fundamental_metrics.items():
                if "value" in data and "industry_avg" in data:
                    metrics.append(name.replace("_", " ").title())
                    stock_values.append(data["value"])
                    industry_values.append(data["industry_avg"])
            
            if metrics and stock_values and industry_values:
                chart = create_fundamental_comparison_chart(
                    metrics=metrics,
                    stock_values=stock_values,
                    benchmark_values=[0] * len(metrics),  # Placeholder
                    industry_values=industry_values
                )
                
                components = [{"type": "chart", "config": chart}]
                
                # Add detailed cards for each fundamental metric
                for name, data in self.fundamental_metrics.items():
                    if "value" not in data:
                        continue
                        
                    display_name = name.replace("_", " ").title()
                    value = data["value"]
                    industry_avg = data.get("industry_avg")
                    
                    interpretation = self._get_fundamental_interpretation(name, value, industry_avg)
                    
                    trend_direction = "neutral"
                    if industry_avg is not None:
                        if name in ["pe_ratio", "debt_to_equity"]:  # Lower is better
                            trend_direction = "up" if value < industry_avg else "down"
                        else:  # Higher is better
                            trend_direction = "up" if value > industry_avg else "down"
                    
                    card = InsightCard(
                        title=display_name,
                        value=f"{value:.2f}",
                        interpretation=interpretation,
                        trend_direction=trend_direction
                    )
                    
                    # Add detailed explanation based on the metric
                    card.add_tooltip(self._get_fundamental_tooltip(name))
                    
                    components.append({"type": "card", "config": card.to_dict()})
            else:
                components = []
        
        self.add_section("fundamental", "Fundamental Analysis", components)
    
    def build_sentiment_section(self) -> None:
        """Build the sentiment analysis section of the dashboard."""
        if not self.sentiment_data:
            return
            
        components = []
        
        # Create sentiment gauge
        overall_score = self.sentiment_data.get("overall_score", 0)
        sentiment_gauge = create_sentiment_gauge(overall_score)
        components.append({"type": "gauge", "config": sentiment_gauge})
        
        # Sentiment description card
        sentiment_level = "Neutral"
        if overall_score < -0.5:
            sentiment_level = "Very Negative"
        elif overall_score < -0.1:
            sentiment_level = "Negative"
        elif overall_score > 0.5:
            sentiment_level = "Very Positive"
        elif overall_score > 0.1:
            sentiment_level = "Positive"
            
        sentiment_card = InsightCard(
            title="Market Sentiment",
            value=sentiment_level,
            interpretation=self.sentiment_data.get("summary", "Based on recent news and social media"),
            trend_direction="up" if overall_score > 0 else "down" if overall_score < 0 else "neutral"
        )
        sentiment_card.add_tooltip("Market sentiment reflects the overall feeling or tone of investors toward a stock based on news, social media, and analyst opinions.")
        components.append({"type": "card", "config": sentiment_card.to_dict()})
        
        # Add news highlights in advanced mode
        if self.view_mode == "advanced" and "news_items" in self.sentiment_data:
            news_items = self.sentiment_data["news_items"][:5]  # Top 5 news items
            for item in news_items:
                components.append({
                    "type": "news",
                    "config": {
                        "title": item.get("title", ""),
                        "source": item.get("source", ""),
                        "date": item.get("date", ""),
                        "sentiment": item.get("sentiment", 0),
                        "url": item.get("url", "")
                    }
                })
        
        self.add_section("sentiment", "Sentiment Analysis", components)
    
    def build_integrated_section(self) -> None:
        """Build an integrated analysis section with combined insights."""
        # Only create for advanced view
        if self.view_mode != "advanced":
            return
            
        components = []
        
        # Create an integrated score card if available
        if "integrated_score" in self.sentiment_data:
            score = self.sentiment_data["integrated_score"]
            
            score_status = "Neutral"
            if score < 30:
                score_status = "Bearish"
            elif score < 45:
                score_status = "Slightly Bearish"
            elif score > 70:
                score_status = "Bullish"
            elif score > 55:
                score_status = "Slightly Bullish"
                
            integrated_card = InsightCard(
                title="Integrated Analysis Score",
                value=f"{score}/100",
                interpretation=f"Overall outlook: {score_status}",
                trend_direction="up" if score > 50 else "down" if score < 50 else "neutral"
            )
            integrated_card.add_tooltip("Integrated Analysis Score combines technical, fundamental, and sentiment indicators to provide a comprehensive evaluation of the stock.")
            components.append({"type": "card", "config": integrated_card.to_dict()})
            
        self.add_section("integrated", "Integrated Analysis", components)
    
    def build_dashboard(self) -> Dict[str, Any]:
        """Build the complete dashboard with all sections."""
        # Clear existing sections
        self.sections = {}
        
        # Build all sections
        self.build_price_section()
        self.build_technical_section()
        self.build_fundamental_section()
        self.build_sentiment_section()
        self.build_integrated_section()
        
        return self.generate_dashboard_config()
    
    def _calculate_technical_health(self) -> Dict[str, str]:
        """Calculate technical health status based on indicators."""
        # Initialize with a neutral status
        health = {
            "status": "Neutral",
            "interpretation": "Technical indicators show mixed signals",
            "trend_direction": "neutral"
        }
        
        # Count positive and negative signals
        positive_signals = 0
        negative_signals = 0
        
        # Check RSI
        if "rsi" in self.technical_indicators and self.technical_indicators["rsi"]:
            rsi = self.technical_indicators["rsi"][-1]
            if rsi < 30:
                negative_signals += 1
            elif rsi > 70:
                positive_signals += 1
                
        # Check MACD
        if "macd" in self.technical_indicators and "macd_signal" in self.technical_indicators:
            if len(self.technical_indicators["macd"]) > 1 and len(self.technical_indicators["macd_signal"]) > 1:
                macd = self.technical_indicators["macd"][-1]
                macd_signal = self.technical_indicators["macd_signal"][-1]
                macd_prev = self.technical_indicators["macd"][-2]
                
                if macd > macd_signal and macd > macd_prev:
                    positive_signals += 1
                elif macd < macd_signal and macd < macd_prev:
                    negative_signals += 1
        
        # Check moving averages
        if "moving_averages" in self.technical_indicators:
            for ma_name, ma_values in self.technical_indicators["moving_averages"].items():
                if not ma_values or len(ma_values) < 2:
                    continue
                    
                if ma_values[-1] > ma_values[-2]:
                    positive_signals += 1
                else:
                    negative_signals += 1
        
        # Determine overall health
        if positive_signals > negative_signals + 1:
            health = {
                "status": "Strong",
                "interpretation": "Technical indicators suggest bullish momentum",
                "trend_direction": "up"
            }
        elif positive_signals > negative_signals:
            health = {
                "status": "Positive",
                "interpretation": "Technical indicators lean bullish",
                "trend_direction": "up"
            }
        elif negative_signals > positive_signals + 1:
            health = {
                "status": "Weak",
                "interpretation": "Technical indicators suggest bearish momentum",
                "trend_direction": "down"
            }
        elif negative_signals > positive_signals:
            health = {
                "status": "Negative",
                "interpretation": "Technical indicators lean bearish",
                "trend_direction": "down"
            }
            
        return health
    
    def _calculate_financial_health(self) -> Dict[str, str]:
        """Calculate financial health status based on fundamental metrics."""
        # Initialize with a neutral status
        health = {
            "status": "Neutral",
            "interpretation": "Company financials show mixed signals",
            "trend_direction": "neutral"
        }
        
        # Count positive and negative metrics
        positive_metrics = 0
        negative_metrics = 0
        
        # Check key metrics against industry averages
        for name, data in self.fundamental_metrics.items():
            if "value" not in data or "industry_avg" not in data:
                continue
                
            value = data["value"]
            industry_avg = data["industry_avg"]
            
            # For metrics where higher is better
            if name in ["roe", "roa", "profit_margin", "current_ratio"]:
                if value > industry_avg * 1.1:  # 10% above industry
                    positive_metrics += 1
                elif value < industry_avg * 0.9:  # 10% below industry
                    negative_metrics += 1
            
            # For metrics where lower is better
            elif name in ["pe_ratio", "debt_to_equity"]:
                if value < industry_avg * 0.9:
                    positive_metrics += 1
                elif value > industry_avg * 1.1:
                    negative_metrics += 1
        
        # Determine overall health
        if positive_metrics > negative_metrics + 1:
            health = {
                "status": "Strong",
                "interpretation": "Fundamentals outperform industry standards",
                "trend_direction": "up"
            }
        elif positive_metrics > negative_metrics:
            health = {
                "status": "Positive",
                "interpretation": "Fundamentals above industry average",
                "trend_direction": "up"
            }
        elif negative_metrics > positive_metrics + 1:
            health = {
                "status": "Weak",
                "interpretation": "Fundamentals underperform industry standards",
                "trend_direction": "down"
            }
        elif negative_metrics > positive_metrics:
            health = {
                "status": "Negative",
                "interpretation": "Fundamentals below industry average",
                "trend_direction": "down"
            }
            
        return health
    
    def _get_indicator_interpretation(self, indicator: str, value: float) -> str:
        """Get interpretation text for a technical indicator."""
        if indicator == "rsi":
            if value < 30:
                return "Potentially oversold"
            elif value > 70:
                return "Potentially overbought"
            else:
                return "Within normal range"
                
        elif indicator == "macd":
            return "Momentum indicator"
            
        elif indicator == "bollinger_upper":
            return "Upper volatility band"
            
        elif indicator == "bollinger_lower":
            return "Lower volatility band"
            
        elif "ma" in indicator or "ema" in indicator:
            return f"{indicator.upper()} trendline"
            
        return "Technical indicator"
    
    def _get_fundamental_interpretation(self, metric: str, value: float, 
                                      industry_avg: Optional[float] = None) -> str:
        """Get interpretation text for a fundamental metric."""
        if industry_avg is None:
            return "No industry comparison available"
            
        percent_diff = ((value - industry_avg) / industry_avg * 100) if industry_avg != 0 else 0
        
        # Format the difference text
        diff_text = f"{abs(percent_diff):.1f}% "
        diff_text += "above" if percent_diff > 0 else "below"
        diff_text += " industry average"
        
        return diff_text
    
    def _get_fundamental_tooltip(self, metric: str) -> str:
        """Get detailed tooltip explanation for a fundamental metric."""
        tooltips = {
            "pe_ratio": "Price-to-Earnings (P/E) ratio compares the stock price to the company's earnings per share. Lower values may indicate undervaluation.",
            "roe": "Return on Equity (ROE) measures how efficiently a company uses its equity to generate profits. Higher values often indicate stronger performance.",
            "roa": "Return on Assets (ROA) measures how efficiently a company uses its assets to generate profits. Higher values suggest better asset utilization.",
            "profit_margin": "Profit margin represents the percentage of revenue that translates into profit. Higher margins indicate more efficient cost management.",
            "debt_to_equity": "Debt-to-Equity ratio shows the balance between debt and equity financing. Lower values suggest less financial risk.",
            "current_ratio": "Current Ratio measures the company's ability to pay short-term obligations. Higher values indicate better short-term financial health.",
            "quick_ratio": "Quick Ratio (Acid-Test) measures a company's ability to pay short-term obligations using its most liquid assets."
        }
        
        return tooltips.get(metric, "Financial metric used to evaluate company performance")


def create_apple_dashboard(view_mode: str = "basic") -> Dict[str, Any]:
    """
    Create a sample Apple dashboard with mockup data.
    
    Args:
        view_mode: 'basic' or 'advanced'
        
    Returns:
        Complete dashboard configuration
    """
    # Create dashboard instance
    dashboard = StockDashboard("AAPL", "Apple Inc.", view_mode)
    
    # Sample price data (last 30 days)
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
    
    # Mock price data with a realistic pattern
    base_price = 180.0
    prices = []
    for i in range(30):
        change = (i % 5 - 2) * 0.5  # Create some cyclical patterns
        random_factor = (i % 7) * 0.3  # Add some randomness
        price = base_price + change + random_factor
        prices.append(price)
    
    # Sample volume data
    volumes = [int(5000000 + (i % 5) * 1000000) for i in range(30)]
    
    # Set the data
    dashboard.set_price_data(dates, prices, volumes)
    
    # Sample technical indicators
    ma50 = [p * 0.98 for p in prices]  # 50-day MA slightly below price
    ma200 = [p * 0.95 for p in prices]  # 200-day MA further below
    rsi = [45 + (i % 10) for i in range(30)]  # RSI between 45-55
    
    dashboard.set_technical_indicators({
        "rsi": rsi,
        "macd": [0.5 + (i % 5) * 0.1 for i in range(30)],
        "macd_signal": [0.4 + (i % 5) * 0.1 for i in range(30)],
        "moving_averages": {
            "MA50": ma50,
            "MA200": ma200
        }
    })
    
    # Sample fundamental metrics
    dashboard.set_fundamental_metrics({
        "pe_ratio": {"value": 28.5, "industry_avg": 25.0},
        "roe": {"value": 0.35, "industry_avg": 0.28},
        "profit_margin": {"value": 0.22, "industry_avg": 0.18},
        "debt_to_equity": {"value": 1.2, "industry_avg": 1.5},
        "current_ratio": {"value": 1.8, "industry_avg": 1.5}
    })
    
    # Sample sentiment data
    dashboard.set_sentiment_data({
        "overall_score": 0.65,
        "summary": "Recent iPhone sales data and positive analyst coverage contribute to bullish sentiment",
        "news_items": [
            {
                "title": "Apple Reports Strong Q3 Results",
                "source": "Financial Times",
                "date": dates[5],
                "sentiment": 0.8,
                "url": "https://example.com/news1"
            },
            {
                "title": "New iPhone Pro Max Sets Sales Record",
                "source": "Tech Today",
                "date": dates[3],
                "sentiment": 0.9,
                "url": "https://example.com/news2"
            },
            {
                "title": "Apple Faces Supply Chain Challenges",
                "source": "Wall Street Journal",
                "date": dates[7],
                "sentiment": -0.2,
                "url": "https://example.com/news3"
            }
        ],
        "integrated_score": 72
    })
    
    # Build and return the dashboard
    return dashboard.build_dashboard()
