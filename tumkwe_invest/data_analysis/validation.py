"""
Validation module for testing data analysis components.

Provides utilities for validating technical indicators, backtesting, and comparing with external data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import matplotlib.pyplot as plt
from .technical_analysis import TechnicalAnalyzer
from .fundamental_analysis import FundamentalAnalyzer
from .sentiment_analysis import SentimentAnalyzer
from .integrated_analysis import IntegratedAnalyzer


class AnalysisValidator:
    """
    Validates data analysis components against reference data or expected behaviors.
    """
    
    @staticmethod
    def validate_technical_indicators(
        price_data: pd.DataFrame,
        reference_data: Optional[pd.DataFrame] = None,
        external_source: str = "TradingView"
    ) -> Dict[str, Any]:
        """
        Validate technical indicators against reference data or expected statistical properties.
        
        Args:
            price_data (pd.DataFrame): Price data for indicator calculation
            reference_data (pd.DataFrame, optional): Reference data to validate against
            external_source (str): Source name if reference data is from external system
            
        Returns:
            Dict: Validation results with metrics for each indicator
        """
        # Initialize technical analyzer
        analyzer = TechnicalAnalyzer(price_data)
        
        # Calculate all indicators
        analyzer.calculate_all_indicators()
        
        # Validate against reference data if provided
        validation_results = analyzer.validate_indicators(reference_data)
        
        # Add summary statistics
        if validation_results:
            matched = sum(1 for result in validation_results.values() 
                         if isinstance(result, dict) and result.get("matching", False))
            total = sum(1 for result in validation_results.values() if isinstance(result, dict))
            
            validation_summary = {
                "matched_indicators": matched,
                "total_indicators": total,
                "match_percentage": (matched / total) * 100 if total > 0 else 0,
                "external_source": external_source,
                "details": validation_results
            }
        else:
            validation_summary = {
                "matched_indicators": 0,
                "total_indicators": 0,
                "match_percentage": 0,
                "message": "No reference data provided, only statistical validation performed"
            }
            
        return validation_summary
    
    @staticmethod
    def validate_sentiment_model(
        test_dataset: List[Dict[str, str]],
        model_type: str = "ensemble"
    ) -> Dict[str, Any]:
        """
        Validate sentiment analysis model against labeled test data.
        
        Args:
            test_dataset (List[Dict]): Test data with text and sentiment labels
            model_type (str): Type of sentiment model to validate
            
        Returns:
            Dict: Validation metrics including accuracy, precision, recall, F1
        """
        analyzer = SentimentAnalyzer(model_type=model_type)
        metrics = analyzer.validate_accuracy(test_dataset)
        
        return {
            "model_type": model_type,
            "overall_accuracy": metrics["accuracy"],
            "class_metrics": metrics["class_metrics"],
            "test_size": len(test_dataset)
        }
    
    @staticmethod
    def compare_recommendations(
        price_data: pd.DataFrame,
        financial_data: Dict[str, Any],
        news_articles: List[Dict],
        external_recommendations: Dict[str, str],
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Compare integrated analysis recommendations with external analyst recommendations.
        
        Args:
            price_data (pd.DataFrame): Historical price data
            financial_data (Dict): Company financial data
            news_articles (List[Dict]): Recent news articles about the company
            external_recommendations (Dict): External analyst recommendations
            weights (Dict, optional): Custom weights for analysis components
            
        Returns:
            Dict: Comparison results between model and external recommendations
        """
        # Initialize analyzers
        technical = TechnicalAnalyzer(price_data)
        fundamental = FundamentalAnalyzer(financial_data)
        sentiment = SentimentAnalyzer(model_type="ensemble")
        
        # Calculate indicators and metrics
        technical.calculate_all_indicators()
        fundamental.calculate_all_metrics()
        sentiment.analyze_sources(news_articles)
        
        # Create integrated analyzer
        integrated = IntegratedAnalyzer(
            technical_analyzer=technical,
            fundamental_analyzer=fundamental,
            sentiment_analyzer=sentiment,
            weights=weights
        )
        
        # Get recommendation
        result = integrated.calculate_integrated_score()
        
        # Compare with external recommendations
        comparisons = {}
        for source, recommendation in external_recommendations.items():
            # Map external recommendations to same scale
            rec_map = {
                "strong buy": 1.0,
                "buy": 0.5,
                "hold": 0.0,
                "neutral": 0.0,
                "sell": -0.5,
                "strong sell": -1.0
            }
            
            # Get numeric values for comparison
            model_score = result["score"]
            external_score = rec_map.get(recommendation.lower(), 0.0)
            
            # Calculate agreement
            difference = abs(model_score - external_score)
            agreement_level = "high" if difference < 0.25 else ("medium" if difference < 0.75 else "low")
            
            comparisons[source] = {
                "model_recommendation": result["recommendation"],
                "external_recommendation": recommendation,
                "agreement_level": agreement_level,
                "difference": difference
            }
            
        return {
            "model_recommendation": result["recommendation"],
            "model_score": result["score"],
            "external_comparisons": comparisons,
            "component_scores": {
                "technical_score": result["component_scores"]["technical"]["score"],
                "fundamental_score": result["component_scores"]["fundamental"]["score"],
                "sentiment_score": result["component_scores"]["sentiment"]["score"]
            }
        }
    
    @staticmethod
    def visualize_backtest(
        price_data: pd.DataFrame,
        window_size: int = 30,
        step_size: int = 5,
        plot_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run backtesting and visualize results.
        
        Args:
            price_data (pd.DataFrame): Historical price data
            window_size (int): Size of rolling window for backtesting
            step_size (int): Steps to move forward between test windows
            plot_file (str, optional): Path to save the visualization plot
            
        Returns:
            Dict: Backtest results and metrics
        """
        # Initialize technical analyzer (only using technical for backtesting)
        technical = TechnicalAnalyzer(price_data)
        technical.calculate_all_indicators()
        
        # Create integrated analyzer with only technical component
        integrated = IntegratedAnalyzer(
            technical_analyzer=technical,
            weights={"technical": 1.0, "fundamental": 0.0, "sentiment": 0.0}
        )
        
        # Run backtest
        backtest_results = integrated.backtest(
            price_data, 
            window_size=window_size,
            step_size=step_size
        )
        
        # Visualize if needed
        if plot_file and hasattr(price_data, "index") and "detailed_results" in backtest_results:
            plt.figure(figsize=(15, 10))
            
            # Plot price data
            ax1 = plt.subplot(2, 1, 1)
            ax1.plot(price_data.index, price_data["close"], label="Price")
            
            # Plot buy/sell signals
            for result in backtest_results["detailed_results"]:
                date = result["date"]
                if result["score"] > 0.3:  # Buy signal
                    ax1.scatter(date, price_data.loc[date, "close"], 
                                color="green", marker="^", s=100)
                elif result["score"] < -0.3:  # Sell signal
                    ax1.scatter(date, price_data.loc[date, "close"], 
                                color="red", marker="v", s=100)
            
            ax1.set_title("Price Chart with Trading Signals")
            ax1.legend()
            
            # Plot recommendation scores
            ax2 = plt.subplot(2, 1, 2)
            dates = [r["date"] for r in backtest_results["detailed_results"]]
            scores = [r["score"] for r in backtest_results["detailed_results"]]
            correct = [r["correct_direction"] for r in backtest_results["detailed_results"]]
            
            # Color-code by correctness
            for i, (date, score, is_correct) in enumerate(zip(dates, scores, correct)):
                color = "green" if is_correct else "red"
                ax2.bar(i, score, color=color, alpha=0.7)
            
            ax2.set_title("Model Recommendation Scores (Green = Correct, Red = Incorrect)")
            ax2.set_xticks(range(0, len(dates), max(1, len(dates)//10)))
            ax2.set_xticklabels([dates[i].strftime('%Y-%m-%d') if hasattr(dates[i], 'strftime') 
                                else str(dates[i]) 
                                for i in range(0, len(dates), max(1, len(dates)//10))],
                               rotation=45)
            
            plt.tight_layout()
            plt.savefig(plot_file)
            plt.close()
        
        return backtest_results
