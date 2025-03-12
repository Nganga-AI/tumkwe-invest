"""
Tests for the validation module of the data analysis package.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import tempfile
from unittest.mock import patch, MagicMock

from data_analysis.validation import AnalysisValidator
from data_analysis.technical_analysis import TechnicalAnalyzer
from data_analysis.fundamental_analysis import FundamentalAnalyzer
from data_analysis.sentiment_analysis import SentimentAnalyzer
from data_analysis.integrated_analysis import IntegratedAnalyzer


class TestAnalysisValidator(unittest.TestCase):
    """Test cases for AnalysisValidator class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create sample price data
        dates = pd.date_range(start='2020-01-01', periods=100, freq='D')
        self.price_data = pd.DataFrame({
            'open': np.random.normal(100, 5, 100),
            'high': np.random.normal(105, 5, 100),
            'low': np.random.normal(95, 5, 100),
            'close': np.random.normal(100, 5, 100),
            'volume': np.random.normal(1000000, 200000, 100)
        }, index=dates)
        
        # Create sample reference data with slight differences
        self.reference_data = self.price_data.copy()
        self.reference_data['MA_50'] = self.price_data['close'].rolling(window=50).mean() + 0.0005
        
        # Sample financial data
        self.financial_data = {
            'revenue': [1000000, 1100000, 1200000],
            'profit': [100000, 120000, 130000],
            'assets': 2000000,
            'liabilities': 800000,
            'cash_flow': 300000,
            'eps': 2.5,
            'pe_ratio': 15.0
        }
        
        # Sample news articles
        self.news_articles = [
            {
                'title': 'Company XYZ reports record profits',
                'content': 'Company XYZ announced today that it has achieved record profits in the last quarter, exceeding analyst expectations.'
            },
            {
                'title': 'Market uncertainty affects stocks',
                'content': 'Increasing uncertainty in global markets has led to volatility in stock prices across various sectors.'
            }
        ]
        
        # Sample external recommendations
        self.external_recommendations = {
            'Analyst A': 'Buy',
            'Analyst B': 'Hold',
            'Analyst C': 'Strong Buy'
        }
        
        # Sample test dataset for sentiment analysis
        self.test_sentiment_dataset = [
            {'text': 'The company reported great earnings this quarter.', 'label': 'positive'},
            {'text': 'The stock price fell sharply after the announcement.', 'label': 'negative'},
            {'text': 'The market remained stable throughout the day.', 'label': 'neutral'},
            {'text': 'Investors are concerned about the company\'s debt.', 'label': 'negative'},
            {'text': 'The new product launch was a huge success.', 'label': 'positive'}
        ]

    def test_validate_technical_indicators(self):
        """Test validation of technical indicators."""
        # Test with reference data
        result = AnalysisValidator.validate_technical_indicators(
            self.price_data,
            reference_data=self.reference_data
        )
        
        # Check for expected keys in the result
        self.assertIn('matched_indicators', result)
        self.assertIn('total_indicators', result)
        self.assertIn('match_percentage', result)
        
        # Test without reference data
        result_no_ref = AnalysisValidator.validate_technical_indicators(self.price_data)
        self.assertIn('message', result_no_ref)

    def test_validate_sentiment_model(self):
        """Test validation of sentiment analysis model."""
        # Patch the SentimentAnalyzer.validate_accuracy method to avoid actual model loading
        with patch('data_analysis.sentiment_analysis.SentimentAnalyzer.validate_accuracy') as mock_validate:
            # Mock return value for the validate_accuracy method
            mock_validate.return_value = {
                'accuracy': 0.85,
                'class_metrics': {
                    'positive': {'precision': 0.9, 'recall': 0.85, 'f1_score': 0.87},
                    'negative': {'precision': 0.8, 'recall': 0.75, 'f1_score': 0.77},
                    'neutral': {'precision': 0.7, 'recall': 0.65, 'f1_score': 0.67}
                }
            }
            
            # Test with ensemble model type
            result = AnalysisValidator.validate_sentiment_model(
                self.test_sentiment_dataset,
                model_type='ensemble'
            )
            
            # Check structure of result
            self.assertEqual(result['model_type'], 'ensemble')
            self.assertEqual(result['overall_accuracy'], 0.85)
            self.assertEqual(result['test_size'], len(self.test_sentiment_dataset))
            self.assertIn('class_metrics', result)

    def test_compare_recommendations(self):
        """Test comparison of model recommendations with external analyst recommendations."""
        # Patch IntegratedAnalyzer calculate_integrated_score method
        with patch('data_analysis.integrated_analysis.IntegratedAnalyzer.calculate_integrated_score') as mock_calculate:
            # Mock return value for the calculate_integrated_score method
            mock_calculate.return_value = {
                'recommendation': 'Buy',
                'score': 0.7,
                'component_scores': {
                    'technical': {'score': 0.6, 'contribution': 0.24},
                    'fundamental': {'score': 0.8, 'contribution': 0.32},
                    'sentiment': {'score': 0.5, 'contribution': 0.14}
                }
            }
            
            # Test comparison
            result = AnalysisValidator.compare_recommendations(
                self.price_data,
                self.financial_data,
                self.news_articles,
                self.external_recommendations
            )
            
            # Check structure of result
            self.assertEqual(result['model_recommendation'], 'Buy')
            self.assertEqual(result['model_score'], 0.7)
            self.assertIn('external_comparisons', result)
            self.assertIn('component_scores', result)

    def test_visualize_backtest(self):
        """Test backtesting visualization."""
        # Create a temporary file for the plot
        with tempfile.NamedTemporaryFile(suffix='.png') as temp_file:
            # Patch IntegratedAnalyzer backtest method
            with patch('data_analysis.integrated_analysis.IntegratedAnalyzer.backtest') as mock_backtest:
                # Create sample dates for backtest results
                dates = pd.date_range(start='2020-01-01', periods=10, freq='D')
                
                # Mock return value for the backtest method
                mock_backtest.return_value = {
                    'overall_accuracy': 0.7,
                    'profitable_trades': 7,
                    'total_trades': 10,
                    'detailed_results': [
                        {'date': date, 'score': 0.6 if i % 3 == 0 else -0.4 if i % 3 == 1 else 0.1, 
                         'correct_direction': i % 2 == 0} 
                        for i, date in enumerate(dates)
                    ]
                }
                
                # Test visualization
                result = AnalysisValidator.visualize_backtest(
                    self.price_data,
                    window_size=10,
                    step_size=2,
                    plot_file=temp_file.name
                )
                
                # Verify plot file was created
                self.assertTrue(os.path.exists(temp_file.name))
                
                # Check structure of result
                self.assertIn('overall_accuracy', result)
                self.assertIn('profitable_trades', result)
                self.assertIn('total_trades', result)
                self.assertIn('detailed_results', result)


if __name__ == '__main__':
    unittest.main()
