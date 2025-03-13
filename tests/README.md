# Tests for Tumkwe Invest

This directory contains unit and integration tests for the Tumkwe Invest project.

## Running Tests

### Running All Tests

To run all tests:

```bash
python -m unittest discover tests
```

### Running Specific Tests

To run a specific test file:

```bash
python -m unittest tests.test_models
python -m unittest tests.test_yahoo_finance
```

To run a specific test case:

```bash
python -m unittest tests.test_models.TestModels.test_stock_price
```

## Test Categories

The test suite is organized into several categories:

1. **Unit Tests**: Test individual components in isolation
   - `test_config.py` - Tests for the configuration module
   - `test_models.py` - Tests for data models
   - `test_validation.py` - Tests for data validation functions
   - `test_yahoo_finance.py` - Tests for Yahoo Finance collector
   - `test_yahoo_news.py` - Tests for Yahoo Finance news collector
   - `test_news_collector.py` - Tests for News API collector
   - `test_sec_edgar.py` - Tests for SEC EDGAR collector
   - `test_financial_metrics.py` - Tests for financial metrics collector

2. **Integration Tests**: Test components working together
   - `test_integration.py` - Integration tests for data flow
   - `test_collector_manager.py` - Tests for the collector manager

3. **Performance Tests**: Test system performance under load
   - `test_performance.py` - Performance and scalability tests

4. **Functional Tests**: Test end-to-end functionality
   - `test_unified_collection.py` - Tests for the unified collection script

## Setting Up Test Environment

Before running tests, make sure you have the required environment:

1. Install all dependencies from `requirements.txt`
2. Create a `.env` file with necessary API keys for external services
3. Make sure all external dependencies are installed (e.g., NLTK data)

## Adding New Tests

When adding new tests:

1. Follow the naming convention: `test_*.py` for files and `test_*` for methods
2. Use the `unittest` framework
3. Use mocks for external dependencies
4. Include both positive and negative test cases
5. Document any non-obvious test cases with comments

## Continuous Integration

Tests are run automatically on GitHub Actions whenever changes are pushed to the repository.
