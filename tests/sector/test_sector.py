import unittest
from unittest.mock import patch

# ...existing imports...
from tumkwe_invest.sector import (
    get_sector_industries,
    get_sector_key,
    get_sector_name,
    get_sector_overview,
    get_sector_research_reports,
    get_sector_symbol,
    get_sector_ticker,
    get_sector_top_companies,
    get_sector_top_etfs,
    get_sector_top_mutual_funds,
    list_available_sectors,
)

class DummyDict:
    def to_dict(self):
        return {"dummy": "data"}

class DummyTicker:
    @property
    def info(self):
        return {"info": "dummy_ticker_info"}

class FakeSector:
    def __init__(self, sector_key):
        self.key = f"{sector_key}_key"
        self.name = f"{sector_key}_name"
        self.overview = {"overview": "dummy"}
        self.research_reports = [{"report": "dummy"}]
        self.symbol = f"{sector_key}_symbol"
        self.ticker = DummyTicker()
        self.industries = DummyDict()
        self.top_companies = DummyDict()
        self.top_etfs = {"etfs": "dummy"}
        self.top_mutual_funds = {"mutual_funds": "dummy"}

class TestSectorTools(unittest.TestCase):
    @patch("yfinance.Sector", side_effect=lambda sector_key: FakeSector(sector_key))
    def test_get_sector_industries(self, mock_sector):
        result = get_sector_industries.invoke({"sector_key": "energy"})
        self.assertEqual(result, {"dummy": "data"})
    
    @patch("yfinance.Sector", side_effect=lambda sector_key: FakeSector(sector_key))
    def test_get_sector_key(self, mock_sector):
        result = get_sector_key.invoke({"sector_key": "energy"})
        self.assertEqual(result, "energy_key")
    
    @patch("yfinance.Sector", side_effect=lambda sector_key: FakeSector(sector_key))
    def test_get_sector_name(self, mock_sector):
        result = get_sector_name.invoke({"sector_key": "energy"})
        self.assertEqual(result, "energy_name")
    
    @patch("yfinance.Sector", side_effect=lambda sector_key: FakeSector(sector_key))
    def test_get_sector_overview(self, mock_sector):
        result = get_sector_overview.invoke({"sector_key": "energy"})
        self.assertEqual(result, {"overview": "dummy"})
    
    @patch("yfinance.Sector", side_effect=lambda sector_key: FakeSector(sector_key))
    def test_get_sector_research_reports(self, mock_sector):
        result = get_sector_research_reports.invoke({"sector_key": "energy"})
        self.assertEqual(result, [{"report": "dummy"}])
    
    @patch("yfinance.Sector", side_effect=lambda sector_key: FakeSector(sector_key))
    def test_get_sector_symbol(self, mock_sector):
        result = get_sector_symbol.invoke({"sector_key": "energy"})
        self.assertEqual(result, "energy_symbol")
    
    @patch("yfinance.Sector", side_effect=lambda sector_key: FakeSector(sector_key))
    def test_get_sector_ticker(self, mock_sector):
        result = get_sector_ticker.invoke({"sector_key": "energy"})
        self.assertEqual(result, {"info": "dummy_ticker_info"})
    
    @patch("yfinance.Sector", side_effect=lambda sector_key: FakeSector(sector_key))
    def test_get_sector_top_companies(self, mock_sector):
        result = get_sector_top_companies.invoke({"sector_key": "energy"})
        self.assertEqual(result, {"dummy": "data"})
    
    @patch("yfinance.Sector", side_effect=lambda sector_key: FakeSector(sector_key))
    def test_get_sector_top_etfs(self, mock_sector):
        result = get_sector_top_etfs.invoke({"sector_key": "energy"})
        self.assertEqual(result, {"etfs": "dummy"})
    
    @patch("yfinance.Sector", side_effect=lambda sector_key: FakeSector(sector_key))
    def test_get_sector_top_mutual_funds(self, mock_sector):
        result = get_sector_top_mutual_funds.invoke({"sector_key": "energy"})
        self.assertEqual(result, {"mutual_funds": "dummy"})
    
    def test_list_available_sectors(self):
        result = list_available_sectors.invoke({})
        # Check that a known key exists
        self.assertIn("basic-materials", result)

if __name__ == "__main__":
    unittest.main()
