"""
Tests for fundamental analysis functionality.
"""
import unittest

from tumkwe_invest.data_analysis.fundamental_analysis import FundamentalAnalyzer


class TestFundamentalAnalysis(unittest.TestCase):
    """Test case for fundamental analysis functionality."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a sample financial dataset for testing
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
        
        # Create sample industry benchmarks for comparison
        self.sample_industry_benchmarks = {
            'pe_ratio': 20,
            'debt_to_equity': 0.4,
            'return_on_equity': 15,
            'current_ratio': 1.8,
            'profit_margin': 12
        }

    def test_pe_ratio_calculation(self):
        """Test PE ratio calculation."""
        analyzer = FundamentalAnalyzer(self.sample_financial_data)
        pe_ratio = analyzer.calculate_pe_ratio()
        
        # PE = price / EPS
        expected_pe = self.sample_financial_data['current_price'] / self.sample_financial_data['earnings_per_share']
        self.assertEqual(pe_ratio, expected_pe)
        self.assertEqual(analyzer.metrics['pe_ratio'], pe_ratio)

    def test_debt_to_equity_calculation(self):
        """Test debt-to-equity ratio calculation."""
        analyzer = FundamentalAnalyzer(self.sample_financial_data)
        dte = analyzer.calculate_debt_to_equity()
        
        # D/E = total_debt / total_equity
        expected_dte = self.sample_financial_data['total_debt'] / self.sample_financial_data['total_equity']
        self.assertEqual(dte, expected_dte)
        self.assertEqual(analyzer.metrics['debt_to_equity'], dte)

    def test_return_on_equity_calculation(self):
        """Test return on equity calculation."""
        analyzer = FundamentalAnalyzer(self.sample_financial_data)
        roe = analyzer.calculate_return_on_equity()
        
        # ROE = (net_income / total_equity) * 100
        expected_roe = (self.sample_financial_data['net_income'] / self.sample_financial_data['total_equity']) * 100
        self.assertEqual(roe, expected_roe)
        self.assertEqual(analyzer.metrics['return_on_equity'], roe)

    def test_current_ratio_calculation(self):
        """Test current ratio calculation."""
        analyzer = FundamentalAnalyzer(self.sample_financial_data)
        current_ratio = analyzer.calculate_current_ratio()
        
        # Current ratio = current_assets / current_liabilities
        expected_ratio = self.sample_financial_data['current_assets'] / self.sample_financial_data['current_liabilities']
        self.assertEqual(current_ratio, expected_ratio)
        self.assertEqual(analyzer.metrics['current_ratio'], current_ratio)

    def test_profit_margin_calculation(self):
        """Test profit margin calculation."""
        analyzer = FundamentalAnalyzer(self.sample_financial_data)
        margin = analyzer.calculate_profit_margin()
        
        # Profit margin = (net_income / revenue) * 100
        expected_margin = (self.sample_financial_data['net_income'] / self.sample_financial_data['revenue']) * 100
        self.assertEqual(margin, expected_margin)
        self.assertEqual(analyzer.metrics['profit_margin'], margin)

    def test_calculate_all_metrics(self):
        """Test calculation of all metrics at once."""
        analyzer = FundamentalAnalyzer(self.sample_financial_data)
        metrics = analyzer.calculate_all_metrics()
        
        # Check all metrics are calculated
        expected_metrics = ['pe_ratio', 'debt_to_equity', 'return_on_equity', 
                           'current_ratio', 'profit_margin']
        
        for metric in expected_metrics:
            self.assertIn(metric, metrics)

    def test_benchmark_metrics(self):
        """Test benchmarking against industry standards."""
        analyzer = FundamentalAnalyzer(
            self.sample_financial_data, 
            industry_benchmarks=self.sample_industry_benchmarks
        )
        analyzer.calculate_all_metrics()
        benchmark_results = analyzer.benchmark_metrics()
        
        # Check structure of benchmark results
        for metric in self.sample_industry_benchmarks:
            self.assertIn(metric, benchmark_results)
            self.assertIn('company_value', benchmark_results[metric])
            self.assertIn('industry_average', benchmark_results[metric])
            self.assertIn('percent_difference', benchmark_results[metric])
            self.assertIn('performance', benchmark_results[metric])

    def test_assess_valuation(self):
        """Test valuation assessment."""
        analyzer = FundamentalAnalyzer(self.sample_financial_data)
        valuation = analyzer.assess_valuation()
        
        # Check structure of valuation result
        self.assertIn('assessment', valuation)
        self.assertIn('confidence', valuation)
        self.assertIn('factors', valuation)
        
        # Assessment should be one of expected values
        expected_values = [
            'potentially undervalued', 'undervalued', 
            'fairly valued', 'potentially overvalued', 
            'overvalued', 'neutral'
        ]
        self.assertIn(valuation['assessment'], expected_values)

    def test_edge_cases(self):
        """Test edge cases with problematic financial data."""
        # Test with zero values that could cause division by zero
        zero_data = {
            'current_price': 100,
            'earnings_per_share': 0,  # Would cause division by zero in PE ratio
            'total_debt': 1000000,
            'total_equity': 0,  # Would cause division by zero in D/E ratio
            'net_income': 500000,
            'revenue': 0,  # Would cause division by zero in profit margin
            'current_assets': 800000,
            'current_liabilities': 0  # Would cause division by zero in current ratio
        }
        
        analyzer = FundamentalAnalyzer(zero_data)
        
        # These should handle division by zero gracefully
        self.assertEqual(analyzer.calculate_pe_ratio(), float('inf'))
        self.assertEqual(analyzer.calculate_debt_to_equity(), float('inf'))
        self.assertEqual(analyzer.calculate_current_ratio(), float('inf'))
        
        # These should return NaN for division by zero
        import math
        self.assertTrue(math.isnan(analyzer.calculate_profit_margin()))
        self.assertTrue(math.isnan(analyzer.calculate_return_on_equity()))


if __name__ == '__main__':
    unittest.main()
