"""
Fundamental analysis module for evaluating company financial health.

Computes key financial ratios and benchmarks them against industry standards.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List


class FundamentalAnalyzer:
    """
    Analyzes company financial reports and metrics.
    """
    
    def __init__(self, financial_data: Dict[str, Any], industry_benchmarks: Optional[Dict[str, Any]] = None):
        """
        Initialize with financial report data and industry benchmarks.
        
        Args:
            financial_data (Dict): Dictionary containing financial statement data
            industry_benchmarks (Dict, optional): Industry average metrics for comparison
        """
        self.financial_data = financial_data
        self.industry_benchmarks = industry_benchmarks
        self.metrics = {}
        
    def calculate_pe_ratio(self) -> float:
        """
        Calculate Price-to-Earnings ratio.
        
        Returns:
            float: P/E ratio
        """
        price = self.financial_data.get('current_price', 0)
        eps = self.financial_data.get('earnings_per_share', 0)
        
        if eps != 0:
            pe_ratio = price / eps
        else:
            pe_ratio = float('inf')
            
        self.metrics['pe_ratio'] = pe_ratio
        return pe_ratio
    
    def calculate_debt_to_equity(self) -> float:
        """
        Calculate Debt-to-Equity ratio.
        
        Returns:
            float: Debt-to-Equity ratio
        """
        total_debt = self.financial_data.get('total_debt', 0)
        total_equity = self.financial_data.get('total_equity', 0)
        
        if total_equity != 0:
            debt_to_equity = total_debt / total_equity
        else:
            debt_to_equity = float('inf')
            
        self.metrics['debt_to_equity'] = debt_to_equity
        return debt_to_equity
    
    def calculate_return_on_equity(self) -> float:
        """
        Calculate Return on Equity (ROE).
        
        Returns:
            float: ROE as a percentage
        """
        net_income = self.financial_data.get('net_income', 0)
        total_equity = self.financial_data.get('total_equity', 0)
        
        if total_equity != 0:
            roe = (net_income / total_equity) * 100
        else:
            roe = float('nan')
            
        self.metrics['return_on_equity'] = roe
        return roe
    
    def calculate_current_ratio(self) -> float:
        """
        Calculate Current Ratio (liquidity).
        
        Returns:
            float: Current Ratio
        """
        current_assets = self.financial_data.get('current_assets', 0)
        current_liabilities = self.financial_data.get('current_liabilities', 0)
        
        if current_liabilities != 0:
            current_ratio = current_assets / current_liabilities
        else:
            current_ratio = float('inf')
            
        self.metrics['current_ratio'] = current_ratio
        return current_ratio
    
    def calculate_profit_margin(self) -> float:
        """
        Calculate Net Profit Margin.
        
        Returns:
            float: Profit Margin as a percentage
        """
        net_income = self.financial_data.get('net_income', 0)
        revenue = self.financial_data.get('revenue', 0)
        
        if revenue != 0:
            profit_margin = (net_income / revenue) * 100
        else:
            profit_margin = float('nan')
            
        self.metrics['profit_margin'] = profit_margin
        return profit_margin
    
    def benchmark_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Compare calculated metrics with industry benchmarks.
        
        Returns:
            Dict: Comparison results with relative performance
        """
        if not self.industry_benchmarks:
            return {}
            
        benchmark_results = {}
        
        for metric, value in self.metrics.items():
            if metric in self.industry_benchmarks:
                industry_avg = self.industry_benchmarks[metric]
                
                # Calculate percentage difference from industry average
                if industry_avg != 0:
                    percent_diff = ((value - industry_avg) / industry_avg) * 100
                else:
                    percent_diff = float('inf')
                
                # Determine if the difference is good or bad based on the metric
                if metric in ['return_on_equity', 'profit_margin', 'current_ratio']:
                    performance = "better" if value > industry_avg else "worse"
                elif metric in ['pe_ratio', 'debt_to_equity']:
                    performance = "better" if value < industry_avg else "worse"
                else:
                    performance = "unknown"
                
                benchmark_results[metric] = {
                    "company_value": value,
                    "industry_average": industry_avg,
                    "percent_difference": percent_diff,
                    "performance": performance
                }
        
        return benchmark_results
    
    def assess_valuation(self) -> Dict[str, Any]:
        """
        Assess if the stock is overvalued or undervalued.
        
        Returns:
            Dict: Valuation assessment with reasoning
        """
        # Calculate fundamental metrics if not done already
        if not self.metrics:
            self.calculate_all_metrics()
            
        # Benchmark against industry averages if available
        benchmark_results = self.benchmark_metrics()
        
        # Default valuation assessment
        valuation = {
            "assessment": "neutral",
            "confidence": 0,
            "factors": {}
        }
        
        # P/E Ratio analysis
        if 'pe_ratio' in self.metrics:
            pe_ratio = self.metrics['pe_ratio']
            
            if pe_ratio < 0:
                valuation["factors"]["pe_ratio"] = "negative (loss-making company)"
            elif pe_ratio < 15:
                valuation["assessment"] = "potentially undervalued"
                valuation["confidence"] += 1
                valuation["factors"]["pe_ratio"] = "below average P/E ratio"
            elif pe_ratio > 30:
                valuation["assessment"] = "potentially overvalued"
                valuation["confidence"] += 1
                valuation["factors"]["pe_ratio"] = "above average P/E ratio"
                
        # Debt analysis
        if 'debt_to_equity' in self.metrics:
            dte = self.metrics['debt_to_equity']
            if dte > 2:
                valuation["assessment"] = "potentially overvalued"
                valuation["confidence"] += 1
                valuation["factors"]["debt_to_equity"] = "high debt levels"
            elif dte < 0.5:
                valuation["assessment"] = "potentially undervalued" 
                valuation["confidence"] += 0.5
                valuation["factors"]["debt_to_equity"] = "low debt levels"
        
        # Growth metrics can influence valuation
        if 'profit_margin' in self.metrics and 'return_on_equity' in self.metrics:
            pm = self.metrics['profit_margin']
            roe = self.metrics['return_on_equity']
            
            if pm > 20 and roe > 20:
                if valuation["assessment"] == "potentially overvalued":
                    valuation["confidence"] -= 0.5
                else:
                    valuation["assessment"] = "fairly valued"
                valuation["factors"]["growth_metrics"] = "strong profitability may justify higher valuation"
        
        return valuation
    
    def calculate_all_metrics(self) -> Dict[str, float]:
        """
        Calculate all supported financial metrics.
        
        Returns:
            Dict: Dictionary of all calculated metrics
        """
        self.calculate_pe_ratio()
        self.calculate_debt_to_equity()
        self.calculate_return_on_equity()
        self.calculate_current_ratio()
        self.calculate_profit_margin()
        return self.metrics
