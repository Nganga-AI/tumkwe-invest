"""
Integrated analysis module that combines technical, fundamental, and sentiment analyses.

Provides unified scoring and trend assessment based on multiple analysis approaches.
"""

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from .fundamental_analysis import FundamentalAnalyzer
from .sentiment_analysis import SentimentAnalyzer
from .technical_analysis import TechnicalAnalyzer


class IntegratedAnalyzer:
    """
    Combines and weighs results from different analysis approaches.
    """

    def __init__(
        self,
        technical_analyzer: Optional[TechnicalAnalyzer] = None,
        fundamental_analyzer: Optional[FundamentalAnalyzer] = None,
        sentiment_analyzer: Optional[SentimentAnalyzer] = None,
        weights: Optional[Dict[str, float]] = None,
    ):
        """
        Initialize integrated analyzer with individual analyzers.

        Args:
            technical_analyzer (TechnicalAnalyzer, optional): Technical analysis component
            fundamental_analyzer (FundamentalAnalyzer, optional): Fundamental analysis component
            sentiment_analyzer (SentimentAnalyzer, optional): Sentiment analysis component
            weights (Dict[str, float], optional): Custom weights for each analysis type
        """
        self.technical_analyzer = technical_analyzer
        self.fundamental_analyzer = fundamental_analyzer
        self.sentiment_analyzer = sentiment_analyzer

        # Default weights if not provided
        self.weights = (
            weights
            if weights
            else {"technical": 0.40, "fundamental": 0.35, "sentiment": 0.25}
        )

        # Normalize weights to ensure they sum to 1
        weight_sum = sum(self.weights.values())
        if weight_sum != 1.0:
            for key in self.weights:
                self.weights[key] /= weight_sum

        self.results = {}

    def get_technical_score(self) -> Dict[str, Any]:
        """
        Get a normalized score from technical analysis.

        Returns:
            Dict: Score details with value between -1 and 1
        """
        if not self.technical_analyzer:
            return {
                "score": 0,
                "confidence": 0,
                "details": "No technical analyzer provided",
            }

        # Get trend information from technical analyzer
        trend = self.technical_analyzer.detect_trend()

        # Map direction to numeric score
        direction_map = {"bullish": 1, "bearish": -1, "neutral": 0}
        base_score = direction_map.get(trend["direction"], 0)

        # Adjust based on strength (normalize to -1 to 1 range)
        strength = (
            min(max(trend["strength"], -3), 3) / 3
        )  # Clamp to -3 to 3, then normalize

        # Final technical score
        score = base_score * abs(strength) if strength != 0 else 0

        # Confidence based on available indicators
        indicator_count = len(self.technical_analyzer.indicators)
        confidence = min(
            indicator_count / 5, 1.0
        )  # At least 5 indicators for max confidence

        return {
            "score": score,
            "confidence": confidence,
            "trend": trend["direction"],
            "strength": strength,
            "details": trend["signals"],
        }

    def get_fundamental_score(self) -> Dict[str, Any]:
        """
        Get a normalized score from fundamental analysis.

        Returns:
            Dict: Score details with value between -1 and 1
        """
        if not self.fundamental_analyzer:
            return {
                "score": 0,
                "confidence": 0,
                "details": "No fundamental analyzer provided",
            }

        # Make sure all metrics are calculated
        self.fundamental_analyzer.calculate_all_metrics()

        # Get valuation assessment
        valuation = self.fundamental_analyzer.assess_valuation()

        # Map assessment to numeric score
        assessment_map = {
            "potentially undervalued": 0.75,
            "undervalued": 1.0,
            "fairly valued": 0,
            "potentially overvalued": -0.75,
            "overvalued": -1.0,
            "neutral": 0,
        }

        score = assessment_map.get(valuation["assessment"], 0)

        # Adjust based on confidence
        score *= min(valuation["confidence"], 2) / 2  # Scale by confidence (max 2)

        # Get benchmark comparisons for additional details
        benchmark_results = self.fundamental_analyzer.benchmark_metrics()

        # Calculate confidence based on available metrics
        metrics_count = len(self.fundamental_analyzer.metrics)
        benchmarks_count = len(benchmark_results)

        # Higher confidence if we have both metrics and benchmarks
        confidence = (metrics_count / 5) * 0.7  # 5+ metrics for 70% confidence
        if benchmarks_count > 0:
            confidence += 0.3  # Additional 30% if we have benchmark comparisons

        confidence = min(confidence, 1.0)

        return {
            "score": score,
            "confidence": confidence,
            "valuation": valuation["assessment"],
            "details": valuation["factors"],
            "benchmarks": benchmark_results,
        }

    def get_sentiment_score(self) -> Dict[str, Any]:
        """
        Get a normalized score from sentiment analysis.

        Returns:
            Dict: Score details with value between -1 and 1
        """
        if (
            not self.sentiment_analyzer
            or not hasattr(self.sentiment_analyzer, "results")
            or not self.sentiment_analyzer.results
        ):
            return {
                "score": 0,
                "confidence": 0,
                "details": "No sentiment results available",
            }

        results = self.sentiment_analyzer.results

        if "overall" not in results:
            return {
                "score": 0,
                "confidence": 0,
                "details": "No overall sentiment found",
            }

        overall = results["overall"]

        # Map sentiment to score
        sentiment_map = {"positive": 1.0, "neutral": 0.0, "negative": -1.0}

        score = sentiment_map.get(overall.get("dominant_sentiment", "neutral"), 0)

        # Apply confidence as a multiplier
        confidence = overall.get("confidence", 0.5)
        score *= confidence

        # Additional details about distribution
        distribution = overall.get("distribution", {})

        return {
            "score": score,
            "confidence": confidence,
            "sentiment": overall.get("dominant_sentiment", "neutral"),
            "distribution": distribution,
        }

    def calculate_integrated_score(self) -> Dict[str, Any]:
        """
        Calculate weighted combined score from all analysis types.

        Returns:
            Dict: Overall assessment with details from each analysis type
        """
        technical_result = self.get_technical_score()
        fundamental_result = self.get_fundamental_score()
        sentiment_result = self.get_sentiment_score()

        # Calculate weighted score
        technical_contrib = (
            technical_result["score"]
            * self.weights["technical"]
            * technical_result["confidence"]
        )
        fundamental_contrib = (
            fundamental_result["score"]
            * self.weights["fundamental"]
            * fundamental_result["confidence"]
        )
        sentiment_contrib = (
            sentiment_result["score"]
            * self.weights["sentiment"]
            * sentiment_result["confidence"]
        )

        # Calculate confidence-weighted score
        total_weighted_confidence = (
            self.weights["technical"] * technical_result["confidence"]
            + self.weights["fundamental"] * fundamental_result["confidence"]
            + self.weights["sentiment"] * sentiment_result["confidence"]
        )

        if total_weighted_confidence > 0:
            final_score = (
                technical_contrib + fundamental_contrib + sentiment_contrib
            ) / total_weighted_confidence
        else:
            final_score = 0

        # Normalize to -1 to 1 range
        final_score = max(min(final_score, 1.0), -1.0)

        # Map score to a recommendation
        recommendation = "neutral"
        if final_score >= 0.7:
            recommendation = "strong buy"
        elif final_score >= 0.3:
            recommendation = "buy"
        elif final_score <= -0.7:
            recommendation = "strong sell"
        elif final_score <= -0.3:
            recommendation = "sell"

        # Final confidence is the weighted average of component confidences
        final_confidence = (
            technical_result["confidence"] * self.weights["technical"]
            + fundamental_result["confidence"] * self.weights["fundamental"]
            + sentiment_result["confidence"] * self.weights["sentiment"]
        )

        # Handle conflicting signals
        conflicts = self.detect_conflicts(
            technical_result, fundamental_result, sentiment_result
        )

        self.results = {
            "score": final_score,
            "recommendation": recommendation,
            "confidence": final_confidence,
            "component_scores": {
                "technical": technical_result,
                "fundamental": fundamental_result,
                "sentiment": sentiment_result,
            },
            "conflicts": conflicts,
            "weights": self.weights,
        }

        return self.results

    def detect_conflicts(
        self,
        technical_result: Dict[str, Any],
        fundamental_result: Dict[str, Any],
        sentiment_result: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Detect conflicting signals between different analysis types.

        Args:
            technical_result (Dict): Technical analysis result
            fundamental_result (Dict): Fundamental analysis result
            sentiment_result (Dict): Sentiment analysis result

        Returns:
            List[Dict]: List of detected conflicts with resolution rules
        """
        conflicts = []

        # Check for technical vs fundamental conflicts
        if technical_result["score"] * fundamental_result["score"] < 0:
            if (
                abs(technical_result["score"]) > 0.3
                and abs(fundamental_result["score"]) > 0.3
            ):
                conflicts.append(
                    {
                        "components": ["technical", "fundamental"],
                        "description": f"Technical analysis suggests {technical_result['trend']} trend, but fundamental analysis indicates {fundamental_result['valuation']}",
                        "resolution": "Higher confidence component given more weight",
                        "severity": (
                            "high"
                            if abs(
                                technical_result["score"] - fundamental_result["score"]
                            )
                            > 1.0
                            else "medium"
                        ),
                    }
                )

        # Check for technical vs sentiment conflicts
        if technical_result["score"] * sentiment_result["score"] < 0:
            if (
                abs(technical_result["score"]) > 0.3
                and abs(sentiment_result["score"]) > 0.3
            ):
                conflicts.append(
                    {
                        "components": ["technical", "sentiment"],
                        "description": f"Technical analysis suggests {technical_result['trend']} trend, but sentiment is {sentiment_result['sentiment']}",
                        "resolution": "Technical analysis given priority for short-term decisions",
                        "severity": "medium",
                    }
                )

        # Check for fundamental vs sentiment conflicts
        if fundamental_result["score"] * sentiment_result["score"] < 0:
            if (
                abs(fundamental_result["score"]) > 0.3
                and abs(sentiment_result["score"]) > 0.3
            ):
                conflicts.append(
                    {
                        "components": ["fundamental", "sentiment"],
                        "description": f"Fundamental analysis indicates {fundamental_result['valuation']}, but sentiment is {sentiment_result['sentiment']}",
                        "resolution": "Fundamental analysis given priority for long-term decisions",
                        "severity": "medium",
                    }
                )

        return conflicts

    def backtest(
        self, historical_data: pd.DataFrame, window_size: int = 30, step_size: int = 5
    ) -> Dict[str, Any]:
        """
        Backtest the integrated analysis on historical data.

        Args:
            historical_data (pd.DataFrame): Historical price data with technical and fundamental information
            window_size (int): Size of the rolling window for backtesting
            step_size (int): Steps to move forward between test windows

        Returns:
            Dict: Backtest results with performance metrics
        """
        if len(historical_data) < window_size:
            return {"error": "Insufficient historical data for backtesting"}

        backtest_results = []
        actual_returns = []
        predicted_directions = []

        # Iterate through historical data using rolling windows
        for start_idx in range(0, len(historical_data) - window_size, step_size):
            end_idx = start_idx + window_size

            # Select data for this window
            window_data = historical_data.iloc[start_idx:end_idx]

            # Future returns (to evaluate prediction)
            if (
                end_idx < len(historical_data) - 1
            ):  # Ensure we have future data to compare
                future_return = (
                    historical_data["close"].iloc[end_idx + 1]
                    - window_data["close"].iloc[-1]
                ) / window_data["close"].iloc[-1]
            else:
                future_return = None

            # Create analyzers for this window
            if self.technical_analyzer:
                window_technical = TechnicalAnalyzer(window_data)
                window_technical.calculate_all_indicators()
            else:
                window_technical = None

            # Skip fundamental and sentiment for backtesting if not initialized
            # (would need historical fundamental data and news/sentiment data)

            # Create integrated analyzer for this window
            window_integrated = IntegratedAnalyzer(
                technical_analyzer=window_technical,
                weights={"technical": 1.0, "fundamental": 0.0, "sentiment": 0.0},
            )

            # Calculate score
            result = window_integrated.calculate_integrated_score()

            if future_return is not None:
                # Compare prediction direction with actual return
                predicted_direction = (
                    np.sign(result["score"]) if result["score"] != 0 else 0
                )
                actual_direction = np.sign(future_return) if future_return != 0 else 0

                correct_prediction = predicted_direction == actual_direction

                backtest_results.append(
                    {
                        "date": (
                            window_data.index[-1]
                            if hasattr(window_data, "index")
                            else end_idx
                        ),
                        "score": result["score"],
                        "recommendation": result["recommendation"],
                        "future_return": future_return,
                        "correct_direction": correct_prediction,
                    }
                )

                actual_returns.append(future_return)
                predicted_directions.append(predicted_direction)

        # Calculate overall performance metrics
        correct_predictions = sum(1 for r in backtest_results if r["correct_direction"])
        total_predictions = len(backtest_results)

        accuracy = (
            correct_predictions / total_predictions if total_predictions > 0 else 0
        )

        # Calculate risk-adjusted returns if we had followed the recommendations
        returns = []
        for result in backtest_results:
            # Scale position size by conviction (score magnitude)
            position_size = abs(result["score"])
            # Position direction based on score sign
            position_direction = np.sign(result["score"])
            # Calculate position return
            position_return = (
                position_size * position_direction * result["future_return"]
            )
            returns.append(position_return)

        avg_return = np.mean(returns) if returns else 0
        sharpe = (
            np.mean(returns) / np.std(returns) if returns and np.std(returns) > 0 else 0
        )

        return {
            "accuracy": accuracy,
            "avg_return": avg_return,
            "sharpe_ratio": sharpe,
            "total_predictions": total_predictions,
            "correct_predictions": correct_predictions,
            "detailed_results": backtest_results,
        }
