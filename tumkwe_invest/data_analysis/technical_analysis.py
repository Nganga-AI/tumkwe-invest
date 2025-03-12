"""
Technical analysis module for stock data.

Implements various technical indicators and trend detection algorithms.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple


class TechnicalAnalyzer:
    """
    Analyzes stock price data using technical indicators.
    """
    
    def __init__(self, price_data: pd.DataFrame):
        """
        Initialize with historical price data.
        
        Args:
            price_data (pd.DataFrame): DataFrame with columns including 'close', 'high', 'low', 'volume'
        """
        self.data = price_data
        self.indicators = {}
        
    def calculate_moving_average(self, window: int, column: str = 'close') -> pd.Series:
        """
        Calculate simple moving average for specified window.
        
        Args:
            window (int): Window size for moving average
            column (str): Column to calculate MA for (default: 'close')
            
        Returns:
            pd.Series: Moving average values
        """
        ma = self.data[column].rolling(window=window).mean()
        self.indicators[f'MA_{window}'] = ma
        return ma
    
    def calculate_rsi(self, window: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index.
        
        Args:
            window (int): RSI calculation period (default: 14)
            
        Returns:
            pd.Series: RSI values
        """
        delta = self.data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        self.indicators['RSI'] = rsi
        return rsi
    
    def calculate_macd(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            fast_period (int): Fast EMA period
            slow_period (int): Slow EMA period
            signal_period (int): Signal line period
            
        Returns:
            Tuple: (MACD line, signal line, histogram)
        """
        fast_ema = self.data['close'].ewm(span=fast_period, adjust=False).mean()
        slow_ema = self.data['close'].ewm(span=slow_period, adjust=False).mean()
        
        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        histogram = macd_line - signal_line
        
        self.indicators['MACD_line'] = macd_line
        self.indicators['MACD_signal'] = signal_line
        self.indicators['MACD_histogram'] = histogram
        
        return macd_line, signal_line, histogram
    
    def calculate_bollinger_bands(self, window: int = 20, num_std: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands.
        
        Args:
            window (int): Moving average window
            num_std (float): Number of standard deviations for bands
            
        Returns:
            Tuple: (middle band, upper band, lower band)
        """
        middle_band = self.data['close'].rolling(window=window).mean()
        rolling_std = self.data['close'].rolling(window=window).std()
        
        upper_band = middle_band + (rolling_std * num_std)
        lower_band = middle_band - (rolling_std * num_std)
        
        self.indicators['BB_middle'] = middle_band
        self.indicators['BB_upper'] = upper_band
        self.indicators['BB_lower'] = lower_band
        
        return middle_band, upper_band, lower_band
    
    def detect_trend(self) -> Dict[str, Any]:
        """
        Detect trend direction based on calculated indicators.
        
        Returns:
            Dict: Trend assessment with direction and strength
        """
        # Calculate indicators if they don't exist
        if 'MA_50' not in self.indicators:
            self.calculate_moving_average(50)
        if 'MA_200' not in self.indicators:
            self.calculate_moving_average(200)
        if 'RSI' not in self.indicators:
            self.calculate_rsi()
        
        # Trend detection logic
        latest_close = self.data['close'].iloc[-1]
        ma_50 = self.indicators['MA_50'].iloc[-1]
        ma_200 = self.indicators['MA_200'].iloc[-1]
        rsi = self.indicators['RSI'].iloc[-1]
        
        # Simple trend rules
        trend = {
            "direction": "neutral",
            "strength": 0,
            "signals": {}
        }
        
        # Price above/below moving averages
        if latest_close > ma_50 > ma_200:
            trend["direction"] = "bullish"
            trend["strength"] += 2
            trend["signals"]["moving_averages"] = "bullish"
        elif latest_close < ma_50 < ma_200:
            trend["direction"] = "bearish"
            trend["strength"] -= 2
            trend["signals"]["moving_averages"] = "bearish"
        
        # RSI conditions
        if rsi > 70:
            trend["signals"]["rsi"] = "overbought"
            trend["strength"] -= 1
        elif rsi < 30:
            trend["signals"]["rsi"] = "oversold"
            trend["strength"] += 1
        
        return trend
    
    def validate_indicators(self, reference_data: Optional[pd.DataFrame] = None) -> Dict[str, float]:
        """
        Validate indicator calculations against reference data or expected statistical properties.
        
        Args:
            reference_data (pd.DataFrame, optional): Reference data for validation
            
        Returns:
            Dict: Validation metrics for each indicator
        """
        validation_results = {}
        
        # If reference data is provided, compare calculations
        if reference_data is not None:
            for indicator_name, indicator_values in self.indicators.items():
                if indicator_name in reference_data:
                    # Calculate mean absolute error
                    error = abs(indicator_values - reference_data[indicator_name]).mean()
                    validation_results[indicator_name] = {
                        "mean_abs_error": error,
                        "matching": error < 0.001  # Arbitrary threshold
                    }
        
        # Statistical validation (always performed)
        # For example, RSI should always be between 0 and 100
        if 'RSI' in self.indicators:
            rsi_valid = ((self.indicators['RSI'] >= 0) & (self.indicators['RSI'] <= 100)).all()
            validation_results['RSI_bounds'] = rsi_valid
            
        return validation_results
    
    def calculate_all_indicators(self) -> Dict[str, pd.Series]:
        """
        Calculate all supported technical indicators.
        
        Returns:
            Dict: Dictionary of all calculated indicators
        """
        self.calculate_moving_average(20)
        self.calculate_moving_average(50)
        self.calculate_moving_average(200)
        self.calculate_rsi()
        self.calculate_macd()
        self.calculate_bollinger_bands()
        return self.indicators
