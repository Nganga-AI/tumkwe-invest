"""
Tests for the technical analysis module of the data analysis package.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from data_analysis.technical_analysis import TechnicalAnalyzer


class TestTechnicalAnalyzer(unittest.TestCase):
    """Test cases for TechnicalAnalyzer class."""

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
        
        # Create reference data with known values
        self.reference_data = pd.DataFrame({
            'MA_20': self.price_data['close'].rolling(window=20).mean(),
            'MA_50': self.price_data['close'].rolling(window=50).mean(),
            'RSI': np.random.uniform(30, 70, 100)  # Simplified for testing
        }, index=dates)
        
        # Initialize the analyzer
        self.analyzer = TechnicalAnalyzer(self.price_data)

    def test_calculate_moving_average(self):
        """Test calculation of moving averages."""
        # Calculate moving average
        ma20 = self.analyzer.calculate_moving_average(window=20)
        
        # Check that MA was calculated correctly
        pd.testing.assert_series_equal(
            ma20, 
            self.price_data['close'].rolling(window=20).mean(),
            check_names=False
        )
        
        # Check that it's stored in the indicators dictionary
        self.assertIn('MA_20', self.analyzer.indicators)

    def test_calculate_rsi(self):
        """Test calculation of RSI."""
        # Calculate RSI
        rsi = self.analyzer.calculate_rsi(window=14)
        
        # Check that RSI has the correct length
        self.assertEqual(len(rsi), len(self.price_data))
        
        # Check RSI values are in the correct range (0-100)
        self.assertTrue((rsi.dropna() >= 0).all() and (rsi.dropna() <= 100).all())
        
        # Check that it's stored in the indicators dictionary
        self.assertIn('RSI', self.analyzer.indicators)

    def test_calculate_macd(self):
        """Test calculation of MACD."""
        # Calculate MACD
        macd_line, signal_line, histogram = self.analyzer.calculate_macd(
            fast_period=12, 
            slow_period=26, 
            signal_period=9
        )
        
        # Check that all components have the correct length
        self.assertEqual(len(macd_line), len(self.price_data))
        self.assertEqual(len(signal_line), len(self.price_data))
        self.assertEqual(len(histogram), len(self.price_data))
        
        # Check histogram is the difference between MACD and signal
        pd.testing.assert_series_equal(
            histogram, 
            macd_line - signal_line, 
            check_names=False
        )
        
        # Check that they're stored in the indicators dictionary
        self.assertIn('MACD_line', self.analyzer.indicators)
        self.assertIn('MACD_signal', self.analyzer.indicators)
        self.assertIn('MACD_histogram', self.analyzer.indicators)

    def test_calculate_bollinger_bands(self):
        """Test calculation of Bollinger Bands."""
        # Calculate Bollinger Bands
        middle, upper, lower = self.analyzer.calculate_bollinger_bands(
            window=20, 
            num_std=2.0
        )
        
        # Calculate expected values
        expected_middle = self.price_data['close'].rolling(window=20).mean()
        expected_std = self.price_data['close'].rolling(window=20).std()
        expected_upper = expected_middle + (expected_std * 2.0)
        expected_lower = expected_middle - (expected_std * 2.0)
        
        # Check calculations
        pd.testing.assert_series_equal(middle, expected_middle, check_names=False)
        pd.testing.assert_series_equal(upper, expected_upper, check_names=False)
        pd.testing.assert_series_equal(lower, expected_lower, check_names=False)
        
        # Check that they're stored in the indicators dictionary
        self.assertIn('BB_middle', self.analyzer.indicators)
        self.assertIn('BB_upper', self.analyzer.indicators)
        self.assertIn('BB_lower', self.analyzer.indicators)

    def test_detect_trend(self):
        """Test trend detection."""
        # Calculate necessary indicators first
        self.analyzer.calculate_moving_average(50)
        self.analyzer.calculate_moving_average(200)
        self.analyzer.calculate_rsi()
        
        # Detect trend
        trend = self.analyzer.detect_trend()
        
        # Check that the trend has the expected structure
        self.assertIn('direction', trend)
        self.assertIn('strength', trend)
        self.assertIn('signals', trend)
        
        # Check that direction is one of the expected values
        self.assertIn(trend['direction'], ['bullish', 'bearish', 'neutral'])

    def test_validate_indicators(self):
        """Test validation of indicators."""
        # Calculate all indicators
        self.analyzer.calculate_all_indicators()
        
        # Validate against reference data
        validation_results = self.analyzer.validate_indicators(self.reference_data)
        
        # Check that validation results are produced for indicators in reference data
        for indicator in ['MA_20', 'MA_50']:
            if indicator in self.reference_data:
                self.assertIn(indicator, validation_results)
                
        # Test RSI bounds validation
        self.assertIn('RSI_bounds', validation_results)

    def test_calculate_all_indicators(self):
        """Test calculation of all indicators."""
        # Calculate all indicators
        indicators = self.analyzer.calculate_all_indicators()
        
        # Check that key indicators are present
        expected_indicators = ['MA_20', 'MA_50', 'MA_200', 'RSI', 
                              'MACD_line', 'MACD_signal', 'MACD_histogram',
                              'BB_middle', 'BB_upper', 'BB_lower']
        
        for indicator in expected_indicators:
            self.assertIn(indicator, indicators)
            
        # Check that indicators dictionary is the same object
        self.assertIs(indicators, self.analyzer.indicators)


if __name__ == '__main__':
    unittest.main()
