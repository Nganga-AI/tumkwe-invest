"""
Tests for integrated analysis functionality.
"""
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np

from tumkwe_invest.data_analysis.integrated_analysis import IntegratedAnalyzer
from tumkwe_invest.data_analysis.technical_analysis import TechnicalAnalyzer
from tumkwe_invest.data_analysis.fundamental_analysis import FundamentalAnalyzer
from tumkwe_invest.data_analysis.sentiment_analysis import SentimentAnalyzer


class TestIntegratedAnalysis(unittest.TestCase):
    """Test case for integrated analysis functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a simple price dataset for testing
        dates = pd.date_range(start='2023-01-01', periods=100)
        data = {
            'close': [100 + i for i in range(100)],
            'open': [99 + i for i in range(100)],
            'high': [105 + i for i in range(100)],
            'low': [95 + i for i in range(100)],
            'volume': [1000000 for _ in range(100)]
        }
        self.sample_price_data = pd.DataFrame(data, index=dates)
        
        # Create a mock technical analyzer with predefined behavior
        self.technical_mock = MagicMock(spec=TechnicalAnalyzer)
        self.technical_mock.indicators = {
            'MA_20': self.sample_price_data['close'].rolling(window=20).mean(),
            'MA_50': self.sample_price_data['close'].rolling(window=50).mean(),
            'RSI': pd.Series([60] * len(self.sample_price_data), index=self.sample_price_data.index)
        }
        self.technical_mock.detect_trend.return_value = {
            'direction': 'bullish',
            'strength': 2,
            'signals': {'moving_averages': 'bullish', 'rsi': 'neutral'}
        }
        
        # Create a mock fundamental analyzer with predefined behavior
        self.fundamental_mock = MagicMock(spec=FundamentalAnalyzer)
        self.fundamental_mock.metrics = {
            'pe_ratio': 15,
            'debt_to_equity': 0.5,
            'return_on_equity': 18,
            'current_ratio': 2.0,
            'profit_margin': 15
        }
        self.fundamental_mock.assess_valuation.return_value = {
            'assessment': 'fairly valued',
            'confidence': 1,
            'factors': {'pe_ratio': 'average P/E ratio'}
        }
        self.fundamental_mock.benchmark_metrics.return_value = {
            'pe_ratio': {
                'company_value': 15,
                'industry_average': 18,
                'percent_difference': -16.67,
                'performance': 'better'
            }
        }
        
        # Create a mock sentiment analyzer with predefined behavior
        self.sentiment_mock = MagicMock(spec=SentimentAnalyzer)
        self.sentiment_mock.results = {
            'overall': {
                'dominant_sentiment': 'positive',
                'confidence': 0.8,
                'distribution': {
                    'positive_percent': 70,
                    'neutral_percent': 20,
                    'negative_percent': 10
                }
            }
        }

    def test_init_with_custom_weights(self):
        """Test initialization with custom weights."""
        custom_weights = {'technical': 0.5, 'fundamental': 0.3, 'sentiment': 0.2}
        analyzer = IntegratedAnalyzer(weights=custom_weights)
        
        self.assertEqual(analyzer.weights, custom_weights)
        
        # Test normalization of weights
        unbalanced_weights = {'technical': 5, 'fundamental': 3, 'sentiment': 2}
        analyzer = IntegratedAnalyzer(weights=unbalanced_weights)
        
        self.assertEqual(analyzer.weights['technical'], 0.5)
        self.assertEqual(analyzer.weights['fundamental'], 0.3)
        self.assertEqual(analyzer.weights['sentiment'], 0.2)
        self.assertEqual(sum(analyzer.weights.values()), 1.0)

    def test_get_technical_score(self):
        """Test getting technical analysis score."""
        analyzer = IntegratedAnalyzer(technical_analyzer=self.technical_mock)
        score_result = analyzer.get_technical_score()
        
        self.assertIn('score', score_result)
        self.assertIn('confidence', score_result)
        self.assertIn('trend', score_result)
        self.assertIn('strength', score_result)
        self.assertIn('details', score_result)

    def test_get_fundamental_score(self):
        """Test getting fundamental analysis score."""
        analyzer = IntegratedAnalyzer(fundamental_analyzer=self.fundamental_mock)
        score_result = analyzer.get_fundamental_score()
        
        self.assertIn('score', score_result)
        self.assertIn('confidence', score_result)
        self.assertIn('valuation', score_result)
        self.assertIn('details', score_result)
        self.assertIn('benchmarks', score_result)

    def test_get_sentiment_score(self):
        """Test getting sentiment analysis score."""
        analyzer = IntegratedAnalyzer(sentiment_analyzer=self.sentiment_mock)
        score_result = analyzer.get_sentiment_score()
        
        self.assertIn('score', score_result)
        self.assertIn('confidence', score_result)
        self.assertIn('sentiment', score_result)
        self.assertIn('distribution', score_result)

    def test_calculate_integrated_score(self):
        """Test calculation of integrated score combining all analyzers."""
        analyzer = IntegratedAnalyzer(
            technical_analyzer=self.technical_mock,
            fundamental_analyzer=self.fundamental_mock,
            sentiment_analyzer=self.sentiment_mock
        )
        
        result = analyzer.calculate_integrated_score()
        
        # Check result structure
        self.assertIn('score', result)
        self.assertIn('recommendation', result)
        self.assertIn('confidence', result)
        self.assertIn('component_scores', result)
        self.assertIn('conflicts', result)
        self.assertIn('weights', result)
        
        # Check component scores
        self.assertIn('technical', result['component_scores'])
        self.assertIn('fundamental', result['component_scores'])
        self.assertIn('sentiment', result['component_scores'])
        
        # Recommendation should be one of expected values
        self.assertIn(
            result['recommendation'],
            ['strong buy', 'buy', 'neutral', 'sell', 'strong sell']
        )

    def test_detect_conflicts(self):
        """Test conflict detection between different analysis results."""
        analyzer = IntegratedAnalyzer()
        
        # Create conflicting analyses
        technical_result = {'score': 0.8, 'trend': 'bullish', 'confidence': 0.9}
        fundamental_result = {'score': -0.7, 'valuation': 'overvalued', 'confidence': 0.8}
        sentiment_result = {'score': 0.6, 'sentiment': 'positive', 'confidence': 0.7}
        
        conflicts = analyzer.detect_conflicts(
            technical_result,
            fundamental_result,
            sentiment_result
        )
        
        # Should detect technical vs fundamental conflict
        self.assertGreater(len(conflicts), 0)
        
        # Check if any conflict contains both technical and fundamental components
        has_tech_vs_fund_conflict = False
        for conflict in conflicts:
            if 'technical' in conflict['components'] and 'fundamental' in conflict['components']:
                has_tech_vs_fund_conflict = True
                break
        
        self.assertTrue(has_tech_vs_fund_conflict)

    def test_backtest(self):
        """Test backtesting functionality."""
        # Create a real technical analyzer for this test
        technical = TechnicalAnalyzer(self.sample_price_data)
        technical.calculate_all_indicators()
        
        analyzer = IntegratedAnalyzer(
            technical_analyzer=technical,
            weights={'technical': 1.0, 'fundamental': 0.0, 'sentiment': 0.0}
        )
        
        backtest_results = analyzer.backtest(
            self.sample_price_data, 
            window_size=20,
            step_size=5
        )
        
        # Check backtest results structure
        self.assertIn('accuracy', backtest_results)
        self.assertIn('avg_return', backtest_results)
        self.assertIn('sharpe_ratio', backtest_results)
        self.assertIn('total_predictions', backtest_results)
        self.assertIn('correct_predictions', backtest_results)
        self.assertIn('detailed_results', backtest_results)
        
        # Check that we have backtest results
        self.assertGreater(len(backtest_results['detailed_results']), 0)
        
        # Each detailed result should have these properties
        first_result = backtest_results['detailed_results'][0]
        self.assertIn('date', first_result)
        self.assertIn('score', first_result)
        self.assertIn('recommendation', first_result)
        self.assertIn('future_return', first_result)
        self.assertIn('correct_direction', first_result)


if __name__ == '__main__':
    unittest.main()
