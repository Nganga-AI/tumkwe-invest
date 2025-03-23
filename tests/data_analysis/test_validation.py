"""
Tests for validation functionality.
"""
import unittest
from unittest.mock import MagicMock, patch
import os
import pandas as pd

from tumkwe_invest.data_analysis.validation import AnalysisValidator
from tumkwe_invest.data_analysis.technical_analysis import TechnicalAnalyzer


class TestAnalysisValidator(unittest.TestCase):
    """Test case for validation functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a simple price dataset for testing
        dates = pd.date_range(start='2023-01-01', periods=100)
        data = {
            'close': [100 + i + (i % 10) for i in range(100)],
            'open': [100 + i for i in range(100)],
            'high': [105 + i for i in range(100)],
            'low': [95 + i for i in range(100)],
            'volume': [1000000 for _ in range(100)]
        }
        self.sample_price_data = pd.DataFrame(data, index=dates)
        
        # Create sample financial data
        self.sample_financial_data = {
            'current_price': 100,
            'earnings_per_share': 5,
            'total_debt': 1000000,
            'total_equity': 2000000,
            'net_income': 500000,
            'revenue': 5000000,
            'current_assets': 800000,
            'current_liabilities': 400000
        }
        
        # Create sample news articles
        self.sample_news_articles = [
            {
                'title': 'Company XYZ reports positive earnings',
                'content': 'The earnings were 20% better than expected for the quarter.'
            },
            {
                'title': 'Market outlook remains neutral',
                'content': 'Analysts expect sideways movement in the coming months.'
            }
        ]
        
        # Create a sample dataset for testing sentiment validation
        self.sample_test_dataset = [
            {"text": "The company performed exceptionally well this quarter.", "label": "positive"},
            {"text": "The stock price plummeted after poor earnings.", "label": "negative"},
            {"text": "The market remained stable today.", "label": "neutral"}
        ]
        
        # Create reference data with technical indicators
        analyzer = TechnicalAnalyzer(self.sample_price_data)
        analyzer.calculate_moving_average(50)
        analyzer.calculate_rsi()
        
        # Create reference dataframe with indicators and small differences
        self.reference_data = pd.DataFrame({
            'close': self.sample_price_data['close'],
            'MA_50': analyzer.indicators['MA_50'] * 1.01,  # Introduce small difference
            'RSI': analyzer.indicators['RSI'] * 0.99  # Introduce small difference
        })

    def test_validate_technical_indicators(self):
        """Test validation of technical indicators against reference data."""
        validation_results = AnalysisValidator.validate_technical_indicators(
            self.sample_price_data, 
            reference_data=self.reference_data
        )
        
        # Check validation results structure
        self.assertIn('matched_indicators', validation_results)
        self.assertIn('total_indicators', validation_results)
        self.assertIn('match_percentage', validation_results)
        self.assertIn('external_source', validation_results)
        self.assertIn('details', validation_results)

    @patch('tumkwe_invest.data_analysis.validation.SentimentAnalyzer')
    def test_validate_sentiment_model(self, mock_sentiment_class):
        """Test validation of sentiment model against labeled test data."""
        # Configure the mock
        mock_instance = MagicMock()
        mock_instance.validate_accuracy.return_value = {
            "accuracy": 0.85,
            "class_metrics": {
                "positive": {"precision": 0.9, "recall": 0.8, "f1_score": 0.85},
                "negative": {"precision": 0.8, "recall": 0.9, "f1_score": 0.85},
                "neutral": {"precision": 0.7, "recall": 0.7, "f1_score": 0.7}
            }
        }
        mock_sentiment_class.return_value = mock_instance
        
        validation_results = AnalysisValidator.validate_sentiment_model(
            self.sample_test_dataset,
            model_type="ensemble"
        )
        
        # Check validation results structure
        self.assertIn('model_type', validation_results)
        self.assertIn('overall_accuracy', validation_results)
        self.assertIn('class_metrics', validation_results)
        self.assertIn('test_size', validation_results)
        
        # Verify expected values
        self.assertEqual(validation_results['model_type'], "ensemble")
        self.assertEqual(validation_results['test_size'], len(self.sample_test_dataset))
        self.assertEqual(validation_results['overall_accuracy'], 0.85)

    @patch('tumkwe_invest.data_analysis.validation.TechnicalAnalyzer')
    @patch('tumkwe_invest.data_analysis.validation.FundamentalAnalyzer')
    @patch('tumkwe_invest.data_analysis.validation.SentimentAnalyzer')
    @patch('tumkwe_invest.data_analysis.validation.IntegratedAnalyzer')
    def test_compare_recommendations(self, mock_integrated, mock_sentiment, 
                                   mock_fundamental, mock_technical):
        """Test comparison of model recommendations with external recommendations."""
        # Configure the mocks
        mock_integrated_instance = MagicMock()
        mock_integrated_instance.calculate_integrated_score.return_value = {
            "score": 0.6,
            "recommendation": "buy",
            "component_scores": {
                "technical": {"score": 0.7},
                "fundamental": {"score": 0.5},
                "sentiment": {"score": 0.4}
            }
        }
        mock_integrated.return_value = mock_integrated_instance
        
        external_recommendations = {
            "Analyst A": "buy",
            "Analyst B": "hold",
            "Analyst C": "strong buy"
        }
        
        comparison_results = AnalysisValidator.compare_recommendations(
            self.sample_price_data,
            self.sample_financial_data,
            self.sample_news_articles,
            external_recommendations
        )
        
        # Check comparison results structure
        self.assertIn('model_recommendation', comparison_results)
        self.assertIn('model_score', comparison_results)
        self.assertIn('external_comparisons', comparison_results)
        self.assertIn('component_scores', comparison_results)
        
        # Check external comparisons
        for analyst in external_recommendations.keys():
            self.assertIn(analyst, comparison_results['external_comparisons'])
            self.assertIn('agreement_level', comparison_results['external_comparisons'][analyst])
            self.assertIn('difference', comparison_results['external_comparisons'][analyst])

    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    @patch('tumkwe_invest.data_analysis.validation.TechnicalAnalyzer')
    @patch('tumkwe_invest.data_analysis.validation.IntegratedAnalyzer')
    def test_visualize_backtest(self, mock_integrated, mock_technical, 
                               mock_close, mock_savefig, mock_figure):
        """Test backtesting visualization."""
        # Configure the mocks
        mock_integrated_instance = MagicMock()
        mock_integrated_instance.backtest.return_value = {
            "accuracy": 0.65,
            "avg_return": 0.02,
            "sharpe_ratio": 1.2,
            "total_predictions": 10,
            "correct_predictions": 6,
            "detailed_results": [
                {
                    "date": pd.Timestamp("2023-01-30"),
                    "score": 0.7,
                    "recommendation": "buy",
                    "future_return": 0.03,
                    "correct_direction": True
                },
                {
                    "date": pd.Timestamp("2023-02-05"),
                    "score": -0.5,
                    "recommendation": "sell",
                    "future_return": 0.01,
                    "correct_direction": False
                }
            ]
        }
        mock_integrated.return_value = mock_integrated_instance
        
        # Create temporary file for plot
        temp_plot_file = "test_backtest_plot.png"
        
        backtest_results = AnalysisValidator.visualize_backtest(
            self.sample_price_data,
            window_size=20,
            step_size=5,
            plot_file=temp_plot_file
        )
        
        # Check backtest results structure
        self.assertIn('accuracy', backtest_results)
        self.assertIn('avg_return', backtest_results)
        self.assertIn('sharpe_ratio', backtest_results)
        self.assertIn('detailed_results', backtest_results)
        
        # Check that plot would have been created
        mock_savefig.assert_called_once_with(temp_plot_file)
        mock_close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
