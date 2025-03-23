"""
Tests for technical analysis functionality.
"""
import unittest
import pandas as pd
import numpy as np

from tumkwe_invest.data_analysis.technical_analysis import TechnicalAnalyzer


class TestTechnicalAnalysis(unittest.TestCase):
    """Test case for technical analysis functionality."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a simple price dataset for testing technical indicators
        dates = pd.date_range(start='2023-01-01', periods=100)
        data = {
            'close': [100 + i + (i % 10) for i in range(100)],
            'open': [100 + i for i in range(100)],
            'high': [100 + i + 5 for i in range(100)],
            'low': [100 + i - 5 for i in range(100)],
            'volume': [1000000 + (i * 1000) for i in range(100)]
        }
        self.sample_price_data = pd.DataFrame(data, index=dates)
        
    def test_moving_average_calculation(self):
        """Test calculation of simple moving average."""
        analyzer = TechnicalAnalyzer(self.sample_price_data)
        ma_20 = analyzer.calculate_moving_average(window=20)
        
        # Check MA calculation
        self.assertEqual(len(ma_20), len(self.sample_price_data))
        self.assertTrue(pd.isna(ma_20.iloc[0]))
        self.assertTrue(pd.isna(ma_20.iloc[18]))
        self.assertFalse(pd.isna(ma_20.iloc[19]))
        
        # Verify calculation with manual formula for one point
        window = 20
        idx = 30
        expected_ma = sum(self.sample_price_data['close'][idx-window+1:idx+1]) / window
        self.assertAlmostEqual(ma_20.iloc[idx], expected_ma, delta=0.001)

    def test_rsi_calculation(self):
        """Test calculation of RSI indicator."""
        analyzer = TechnicalAnalyzer(self.sample_price_data)
        rsi = analyzer.calculate_rsi(window=14)
        
        # RSI should be between 0 and 100
        valid_rsi_values = rsi.dropna()
        for val in valid_rsi_values:
            self.assertTrue(0 <= val <= 100)
        
        # First n values should be NaN
        self.assertTrue(pd.isna(rsi.iloc[0]))
        self.assertFalse(pd.isna(rsi.iloc[15]))

    def test_bollinger_bands_calculation(self):
        """Test calculation of Bollinger Bands."""
        analyzer = TechnicalAnalyzer(self.sample_price_data)
        middle, upper, lower = analyzer.calculate_bollinger_bands(window=20, num_std=2.0)
        
        # Check that upper > middle > lower
        valid_idx = 25  # An index where we expect values
        self.assertGreater(upper.iloc[valid_idx], middle.iloc[valid_idx])
        self.assertGreater(middle.iloc[valid_idx], lower.iloc[valid_idx])
        
        # Calculate expected middle band at valid_idx (MA)
        expected_middle = sum(self.sample_price_data['close'][valid_idx-20+1:valid_idx+1]) / 20
        self.assertAlmostEqual(middle.iloc[valid_idx], expected_middle, delta=0.001)

    def test_macd_calculation(self):
        """Test calculation of MACD indicator."""
        analyzer = TechnicalAnalyzer(self.sample_price_data)
        macd_line, signal_line, histogram = analyzer.calculate_macd()
        
        # Check lengths
        self.assertEqual(len(macd_line), len(self.sample_price_data))
        self.assertEqual(len(signal_line), len(self.sample_price_data))
        self.assertEqual(len(histogram), len(self.sample_price_data))
        
        # Check histogram = macd_line - signal_line
        non_na_idx = -1  # Last value should be valid
        self.assertAlmostEqual(
            histogram.iloc[non_na_idx], 
            macd_line.iloc[non_na_idx] - signal_line.iloc[non_na_idx],
            delta=0.001
        )

    def test_calculate_all_indicators(self):
        """Test calculation of all indicators at once."""
        analyzer = TechnicalAnalyzer(self.sample_price_data)
        indicators = analyzer.calculate_all_indicators()
        
        # Check if all expected indicators are present
        expected_indicators = ['MA_20', 'MA_50', 'MA_200', 'RSI', 
                              'MACD_line', 'MACD_signal', 'MACD_histogram',
                              'BB_middle', 'BB_upper', 'BB_lower']
                              
        for indicator in expected_indicators:
            self.assertIn(indicator, indicators)
            self.assertEqual(len(indicators[indicator]), len(self.sample_price_data))

    def test_detect_trend(self):
        """Test trend detection functionality."""
        analyzer = TechnicalAnalyzer(self.sample_price_data)
        analyzer.calculate_all_indicators()
        trend = analyzer.detect_trend()
        
        # Check that trend contains expected keys
        self.assertIn('direction', trend)
        self.assertIn('strength', trend)
        self.assertIn('signals', trend)
        
        # Direction should be one of expected values
        self.assertIn(trend['direction'], ['bullish', 'bearish', 'neutral'])

    def test_validate_indicators(self):
        """Test indicator validation function."""
        analyzer = TechnicalAnalyzer(self.sample_price_data)
        analyzer.calculate_all_indicators()
        
        # Create reference data with slight differences
        reference_data = pd.DataFrame({
            'RSI': analyzer.indicators['RSI'] * 1.001,  # 0.1% difference
            'MA_50': analyzer.indicators['MA_50'] * 0.999  # 0.1% difference
        })
        
        validation_results = analyzer.validate_indicators(reference_data)
        
        # Check validation results structure
        self.assertIn('RSI', validation_results)
        self.assertIn('mean_abs_error', validation_results['RSI'])
        self.assertIn('matching', validation_results['RSI'])
        
        # RSI bounds check should be included
        self.assertIn('RSI_bounds', validation_results)


if __name__ == '__main__':
    unittest.main()
