"""
Tests for the SEC EDGAR collector.
"""

import unittest
from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch

from tumkwe_invest.datacollection.collectors.sec_edgar import (
    _respect_rate_limit,
    download_filing_document,
    get_cik_by_ticker,
    get_recent_filings,
)
from tumkwe_invest.datacollection.models import SECFiling


class TestSECEdgar(unittest.TestCase):
    """Tests for the SEC EDGAR collector."""

    @patch("datacollection.collectors.sec_edgar.requests.get")
    @patch("datacollection.collectors.sec_edgar.os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_get_cik_by_ticker(self, mock_file, mock_exists, mock_get):
        """Test CIK lookup by ticker."""
        # Mock file does not exist
        mock_exists.return_value = False

        # Create mock response
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.text = """
        <html>
            <body>
                <p>CIK: 0000320193 (see all company filings)</p>
            </body>
        </html>
        """

        # Configure the mock
        mock_get.return_value = mock_response

        # Call the function
        result = get_cik_by_ticker("AAPL")

        # Validate the result
        self.assertEqual(result, "0000320193")

        # Check that the result was cached
        mock_file().write.assert_called_once()

    @patch("datacollection.collectors.sec_edgar.requests.get")
    @patch("datacollection.collectors.sec_edgar.get_cik_by_ticker")
    @patch("datacollection.collectors.sec_edgar._respect_rate_limit")
    def test_get_recent_filings(self, mock_respect_rate_limit, mock_get_cik, mock_get):
        """Test getting recent SEC filings."""
        # Configure mock for CIK
        mock_get_cik.return_value = "0000320193"

        # Create mock response for filings
        mock_filings_response = MagicMock()
        mock_filings_response.raise_for_status = MagicMock()
        mock_filings_response.text = """
        <html>
            <body>
                <table>
                    <tr>
                        <td>10-K</td>
                        <td><a href="/Archives/edgar/data/320193/000032019322000108/0000320193-22-000108-index.htm">Form 10-K</a></td>
                        <td>Annual report</td>
                        <td>2022-10-28</td>
                    </tr>
                    <tr>
                        <td>10-Q</td>
                        <td><a href="/Archives/edgar/data/320193/000032019322000070/0000320193-22-000070-index.htm">Form 10-Q</a></td>
                        <td>Quarterly report</td>
                        <td>2022-07-29</td>
                    </tr>
                </table>
            </body>
        </html>
        """

        # Configure the mock
        mock_get.return_value = mock_filings_response

        # Call the function
        results = get_recent_filings("AAPL", filing_types=["10-K", "10-Q"])

        # Validate the results
        self.assertEqual(len(results), 2)

        # Check first filing (10-K)
        self.assertEqual(results[0].company_symbol, "AAPL")
        self.assertEqual(results[0].filing_type, "10-K")
        self.assertEqual(results[0].filing_date.date().isoformat(), "2022-10-28")
        self.assertEqual(results[0].accession_number, "0000320193-22-000108")
        self.assertTrue(results[0].url.endswith("0000320193-22-000108-index.htm"))

        # Check second filing (10-Q)
        self.assertEqual(results[1].company_symbol, "AAPL")
        self.assertEqual(results[1].filing_type, "10-Q")
        self.assertEqual(results[1].filing_date.date().isoformat(), "2022-07-29")
        self.assertEqual(results[1].accession_number, "0000320193-22-000070")
        self.assertTrue(results[1].url.endswith("0000320193-22-000070-index.htm"))

    @patch("datacollection.collectors.sec_edgar.requests.get")
    @patch("datacollection.collectors.sec_edgar.os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("datacollection.collectors.sec_edgar._respect_rate_limit")
    def test_download_filing_document(
        self, mock_respect_rate_limit, mock_file, mock_exists, mock_get
    ):
        """Test downloading SEC filing documents."""
        # Mock file does not exist
        mock_exists.return_value = False

        # Create mock filing
        filing = SECFiling(
            company_symbol="AAPL",
            filing_type="10-K",
            filing_date=datetime(2022, 10, 28),
            accession_number="0000320193-22-000108",
            url="https://www.sec.gov/Archives/edgar/data/320193/000032019322000108/0000320193-22-000108-index.htm",
        )

        # Mock index page response
        mock_index_response = MagicMock()
        mock_index_response.raise_for_status = MagicMock()
        mock_index_response.text = """
        <html>
            <body>
                <table summary="Document Format Files">
                    <tr>
                        <td>1</td>
                        <td>10-K form.htm</td>
                        <td><a href="/Archives/edgar/data/320193/000032019322000108/aapl-20221231.htm">Document</a></td>
                    </tr>
                </table>
            </body>
        </html>
        """

        # Mock document response
        mock_doc_response = MagicMock()
        mock_doc_response.raise_for_status = MagicMock()
        mock_doc_response.text = """
        <html>
            <body>
                <h1>APPLE INC. ANNUAL REPORT</h1>
                <p>Financial information and business overview...</p>
            </body>
        </html>
        """

        # Configure the mock to return different responses
        mock_get.side_effect = [mock_index_response, mock_doc_response]

        # Call the function
        result = download_filing_document(filing)

        # Validate the result
        self.assertIsNotNone(result)
        self.assertIn("APPLE INC. ANNUAL REPORT", result)
        self.assertIn("Financial information", result)

        # Check that the content was cached
        mock_file().write.assert_called_once()

    @patch("time.time")
    @patch("time.sleep")
    def test_respect_rate_limit(self, mock_sleep, mock_time):
        """Test rate limiting functionality."""
        # Configure mocks
        mock_time.side_effect = [100.0, 100.1]  # 0.1 seconds have passed

        # Call the function
        _respect_rate_limit()

        # It shouldn't sleep since this is the first call
        mock_sleep.assert_not_called()

        # Now test a second call that needs to be rate limited
        mock_time.side_effect = [100.11, 100.11]  # Only 0.01 seconds since last call
        _respect_rate_limit()

        # It should sleep to enforce the rate limit
        mock_sleep.assert_called_once()


if __name__ == "__main__":
    unittest.main()
